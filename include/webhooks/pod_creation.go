package webhooks

import (
	"fmt"

	corev1 "k8s.io/api/core/v1"
)

// podCreationHandler extracts pod metadata, adds init container to the target, and creates
// a new tracer pod.
func podCreationHandler(pod corev1.Pod) corev1.Pod {
	// cxtract pod details
	annotations := pod.Annotations
	nodeName := pod.Spec.NodeName // might be empty at creation time

	fmt.Printf("Received Pod %s/%s, Node=%s, Annotations=%v\n",
		pod.Namespace, pod.Name, nodeName, annotations)

	// create the init container to inject
	initContainer := corev1.Container{
		Name:  "custom-init",
		Image: "busybox:latest",
		Command: []string{
			"sh", "-c", "echo Custom init container running...",
		},
	}

	pod.Spec.InitContainers = append(pod.Spec.InitContainers, initContainer)

	return pod
}
