package middlewares

import corev1 "k8s.io/api/core/v1"

const (
	flapKey = "k8s.io/flap"
)

// FilterPodByAnnotation looks for flap key in annotations.
// it returns true if it finds `k8s.io/flap: true` in annotations.
func FilterPodByAnnotation(pod *corev1.Pod) bool {
	if value, ok := pod.Annotations[flapKey]; ok && value == "true" {
		return true
	}

	return false
}
