package admission

import (
	"fmt"

	"github.com/sirupsen/logrus"
	admissionv1 "k8s.io/api/admission/v1"
	corev1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/runtime/serializer"
)

// Admitter is a container for admission logic.
type Admitter struct {
	Codecs  serializer.CodecFactory
	Logger  *logrus.Entry
	Request *admissionv1.AdmissionRequest
}

// Pod extracts a pod from an admission request.
func (a Admitter) Pod() (*corev1.Pod, error) {
	if a.Request.Kind.Kind != "Pod" {
		return nil, fmt.Errorf("only pods are supported here")
	}

	p := corev1.Pod{}
	deserializer := a.Codecs.UniversalDeserializer()
	if _, _, err := deserializer.Decode(a.Request.Object.Raw, nil, &p); err != nil {
		return nil, fmt.Errorf("could not unmarshal pod: %v", err)
	}

	return &p, nil
}
