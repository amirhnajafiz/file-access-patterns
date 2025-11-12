package admission

import (
	"encoding/json"
	"fmt"

	"github.com/sirupsen/logrus"
	admissionv1 "k8s.io/api/admission/v1"
	corev1 "k8s.io/api/core/v1"
)

// Admitter is a container for admission logic.
type Admitter struct {
	Logger  *logrus.Entry
	Request *admissionv1.AdmissionRequest
}

// Pod extracts a pod from an admission request.
func (a Admitter) Pod() (*corev1.Pod, error) {
	if a.Request.Kind.Kind != "Pod" {
		return nil, fmt.Errorf("only pods are supported here")
	}

	p := corev1.Pod{}
	if err := json.Unmarshal(a.Request.Object.Raw, &p); err != nil {
		return nil, err
	}

	return &p, nil
}
