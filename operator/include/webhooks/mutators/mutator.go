package mutators

import (
	"github.com/sirupsen/logrus"
	corev1 "k8s.io/api/core/v1"
)

// Mutator handles the logic of flap operator upon different conditions.
type Mutator struct {
	Logger *logrus.Entry
	Pod    *corev1.Pod
}

// NewMutator returns an initialised instance of Mutator.
func NewMutator(l *logrus.Entry, p *corev1.Pod) *Mutator {
	return &Mutator{Logger: l, Pod: p}
}
