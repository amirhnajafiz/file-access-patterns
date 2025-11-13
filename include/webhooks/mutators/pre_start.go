package mutators

import (
	"encoding/json"
	"fmt"

	"github.com/amirhnajafiz/flap/pkg/templates"
)

// PreStartPatchMutate takes a pod, creates a new tracer instance, and adds
// the init container to the target pod.
func (m Mutator) PreStartPatchMutate() ([]byte, error) {
	logger := m.Logger.WithField("mutator", "pre start patch")
	pod := m.Pod

	logger.WithField("node", pod.Spec.NodeName)
	logger.WithField("pod", pod.Name)
	logger.WithField("namespace", pod.Namespace)
	logger.Debug("received pod")

	// create and start a new tracer

	// create the init container to inject
	initContainer := templates.NewInitContainer("")
	pod.Spec.InitContainers = append(pod.Spec.InitContainers, *initContainer)

	// encode the patch
	patch, err := json.Marshal(pod)
	if err != nil {
		return nil, fmt.Errorf("failed to encode path: %v", err)
	}

	return patch, nil
}
