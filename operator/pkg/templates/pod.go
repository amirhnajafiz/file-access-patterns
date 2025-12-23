package templates

import corev1 "k8s.io/api/core/v1"

func NewPod() *corev1.Pod {
	return &corev1.Pod{}
}
