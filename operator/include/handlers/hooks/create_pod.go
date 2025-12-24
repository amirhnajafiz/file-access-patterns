package hooks

import corev1 "k8s.io/api/core/v1"

func hookOnPodCreate(pod *corev1.Pod) {
	if pod.Labels == nil {
		pod.Labels = make(map[string]string)
	}

	pod.Labels["hook_on_pod"] = "OK"
}
