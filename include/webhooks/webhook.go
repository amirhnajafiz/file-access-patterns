package webhooks

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/sirupsen/logrus"

	admissionv1 "k8s.io/api/admission/v1"
	corev1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/runtime/serializer"
	"k8s.io/apimachinery/pkg/util/jsonmergepatch"
)

func MutatePods(codecs serializer.CodecFactory) func(http.ResponseWriter, *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		logger := logrus.WithField("uri", r.RequestURI)
		logger.Debug("received mutation request")

		in, err := parseRequest(*r)
		if err != nil {
			logger.Error(err)
			http.Error(w, err.Error(), http.StatusBadRequest)
			return
		}

		var (
			admissionReview   admissionv1.AdmissionReview
			admissionResponse admissionv1.AdmissionResponse
		)

		req := in.Request
		if req == nil {
			http.Error(w, "empty request", http.StatusBadRequest)
			return
		}

		if req.Kind.Kind != "Pod" {
			admissionResponse = admissionv1.AdmissionResponse{
				Allowed: true,
			}
		} else {
			var pod corev1.Pod
			deserializer := codecs.UniversalDeserializer()
			if _, _, err := deserializer.Decode(req.Object.Raw, nil, &pod); err != nil {
				http.Error(w, fmt.Sprintf("could not unmarshal pod: %v", err), http.StatusBadRequest)
				return
			}

			// apply mutation (keep before and after state)
			original, _ := json.Marshal(pod)
			pod = podCreationHandler(pod)
			modified, _ := json.Marshal(pod)

			patch, err := jsonmergepatch.CreateThreeWayJSONMergePatch(original, modified, original)
			if err != nil {
				http.Error(w, fmt.Sprintf("failed to create patch: %v", err), http.StatusInternalServerError)
				return
			}

			patchType := admissionv1.PatchTypeJSONPatch
			admissionResponse = admissionv1.AdmissionResponse{
				Allowed:   true,
				Patch:     patch,
				PatchType: &patchType,
			}
		}

		admissionReview.Response = &admissionResponse
		admissionReview.Response.UID = admissionReview.Request.UID

		resp, _ := json.Marshal(admissionReview)
		w.Header().Set("Content-Type", "application/json")
		w.Write(resp)
	}
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
