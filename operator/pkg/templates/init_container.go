package templates

import corev1 "k8s.io/api/core/v1"

func NewInitContainer(path string) *corev1.Container {
	return &corev1.Container{
		Name:  "flap-init-container",
		Image: "busybox:latest",
		Command: []string{
			"sh", "-c", "echo Custom init container running...",
		},
	}
}
