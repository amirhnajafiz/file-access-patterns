package hooks

import (
	"encoding/json"
	"net/http"

	"github.com/amirhnajafiz/flap/pkg/admission"

	"github.com/wI2L/jsondiff"
	admissionv1 "k8s.io/api/admission/v1"
)

func Hook(hookType string, adm *admission.Admitter) *admissionv1.AdmissionReview {
	logger := adm.Logger.WithField("uid", adm.Request.UID)
	logger.Debug("hooked")

	// get the pod, upon any errors skip it to unblock pod creation process
	pod, err := adm.Pod()
	if err != nil {
		logger.Error(err)
		return adm.ReviewResponse(false, http.StatusBadRequest, err.Error())
	}

	// if not annotated with flap skip it
	if value, ok := pod.Annotations["k8s.io/flap"]; !ok || value != "true" {
		return adm.ReviewResponse(true, http.StatusAccepted, "OK")
	}

	// deep copy pod
	mpod := pod.DeepCopy()

	// select the hook based on input
	switch hookType {
	case "create_pod":
		hookOnPodCreate(mpod)
	case "delete_pod":
		hookOnDeletePod(mpod)
	}

	// generate json patch
	patch, err := jsondiff.Compare(pod, mpod)
	if err != nil {
		logger.Error(err)
		return adm.ReviewResponse(false, http.StatusInternalServerError, err.Error())
	}

	// convert to bytes
	patchb, err := json.Marshal(patch)
	if err != nil {
		logger.Error(err)
		return adm.ReviewResponse(false, http.StatusInternalServerError, err.Error())
	}

	logger.Debug("unhooked")

	return adm.PatchReviewResponse(patchb)
}
