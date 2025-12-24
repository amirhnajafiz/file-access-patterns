package hooks

import corev1 "k8s.io/api/core/v1"

func hookOnDeletePod(pod *corev1.Pod) {}
