package webhooks

import (
	"encoding/json"
	"net/http"

	"github.com/amirhnajafiz/flap/include/webhooks/mutators"
	"github.com/amirhnajafiz/flap/pkg/admission"
	admissionv1 "k8s.io/api/admission/v1"
	"k8s.io/apimachinery/pkg/util/jsonmergepatch"
)

// reconcile accepts an admitter and applys the mutation logic by calling mutators.
// it returns an admission review
func reconcile(adm *admission.Admitter) *admissionv1.AdmissionReview {
	logger := adm.Logger.WithField("uid", adm.Request.UID)
	logger.Debug("reconcile begin")

	// get the pod, upon any errors skip it to unblock pod creation process
	pod, err := adm.Pod()
	if err != nil {
		logger.Error(err)
		return admission.ReviewResponse(adm.Request.UID, true, http.StatusAccepted, err.Error())
	}

	// if not annotated with flap skip it
	if value, ok := pod.Annotations["k8s.io/flap"]; !ok || value != "true" {
		return admission.ReviewResponse(adm.Request.UID, true, http.StatusAccepted, "OK")
	}

	// create a new mutator to apply the mutation
	mut := mutators.NewMutator(adm.Logger, pod)

	// apply mutation (keep before and after state)
	original, err := json.Marshal(pod)
	if err != nil {
		logger.Error(err)
		return admission.ReviewResponse(adm.Request.UID, false, http.StatusBadRequest, err.Error())
	}
	modified, err := mut.PreStartPatchMutate()
	if err != nil {
		logger.Error(err)
		return admission.ReviewResponse(adm.Request.UID, false, http.StatusInternalServerError, err.Error())
	}

	// create a patch
	patch, err := jsonmergepatch.CreateThreeWayJSONMergePatch(original, modified, original)
	if err != nil {
		logger.Error(err)
		return admission.ReviewResponse(adm.Request.UID, false, http.StatusInternalServerError, err.Error())
	}

	// return the patch review response
	return admission.PatchReviewResponse(adm.Request.UID, patch)
}
