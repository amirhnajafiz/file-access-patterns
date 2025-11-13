package webhooks

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/amirhnajafiz/flap/include/webhooks/middlewares"
	"github.com/amirhnajafiz/flap/include/webhooks/mutators"
	"github.com/amirhnajafiz/flap/pkg/admission"
	"github.com/sirupsen/logrus"

	admissionv1 "k8s.io/api/admission/v1"
	"k8s.io/apimachinery/pkg/runtime/serializer"
	"k8s.io/apimachinery/pkg/util/jsonmergepatch"
)

func MutatePods(codecs serializer.CodecFactory) func(http.ResponseWriter, *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		// init a new logger instance with request uri
		logger := logrus.WithField("uri", r.RequestURI)
		logger.Debug("received mutation request")

		// extract the admission request
		in, err := parseRequest(*r)
		if err != nil {
			logger.Error(err)
			http.Error(w, err.Error(), http.StatusBadRequest)
			return
		}

		// check the request length
		if in.Request == nil {
			http.Error(w, "empty request", http.StatusBadRequest)
			return
		}

		// create a new admitter
		adm := admission.Admitter{
			Codecs:  codecs,
			Logger:  logger,
			Request: in.Request,
		}

		// call reconcile to get the admission review
		admissionReview := reconcile(&adm)

		// return the admission review response
		resp, _ := json.Marshal(admissionReview)
		w.Header().Set("Content-Type", "application/json")
		w.Write(resp)
	}
}

func reconcile(adm *admission.Admitter) *admissionv1.AdmissionReview {
	// get the pod, if the resouorce is not a pod skip it
	pod, err := adm.Pod()
	if err != nil {
		return admission.ReviewResponse(adm.Request.UID, true, http.StatusAccepted, err.Error())
	}

	// apply the middleware, if not annotated skip it
	if ok := middlewares.FilterPodByAnnotation(pod); !ok {
		return admission.ReviewResponse(adm.Request.UID, true, http.StatusAccepted, "OK")
	}

	// create a new mutator
	mut := mutators.NewMutator(adm.Logger, pod)

	// apply mutation (keep before and after state)
	original, _ := json.Marshal(pod)
	modified, _ := mut.PreStartPatchMutate()

	// create a patch
	patch, err := jsonmergepatch.CreateThreeWayJSONMergePatch(original, modified, original)
	if err != nil {
		adm.Logger.Error(err)
		return admission.ReviewResponse(adm.Request.UID, false, http.StatusInternalServerError, err.Error())
	}

	return admission.PatchReviewResponse(adm.Request.UID, patch)
}

// parseRequest extracts an AdmissionReview from an http.Request if possible.
func parseRequest(r http.Request) (*admissionv1.AdmissionReview, error) {
	if r.Header.Get("Content-Type") != "application/json" {
		return nil, fmt.Errorf("Content-Type: %q should be %q",
			r.Header.Get("Content-Type"), "application/json")
	}

	bodybuf := new(bytes.Buffer)
	bodybuf.ReadFrom(r.Body)
	body := bodybuf.Bytes()

	if len(body) == 0 {
		return nil, fmt.Errorf("admission request body is empty")
	}

	var a admissionv1.AdmissionReview

	if err := json.Unmarshal(body, &a); err != nil {
		return nil, fmt.Errorf("could not parse admission review request: %v", err)
	}

	if a.Request == nil {
		return nil, fmt.Errorf("admission review can't be used: Request field is nil")
	}

	return &a, nil
}
