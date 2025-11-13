package mutators

import (
	"encoding/json"
	"fmt"

	corev1 "k8s.io/api/core/v1"
)

func (m Mutator) PreStartPatchMutate() ([]byte, error) {
	pod := m.Pod

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

	patch, _ := json.Marshal(pod)

	return patch, nil
}
