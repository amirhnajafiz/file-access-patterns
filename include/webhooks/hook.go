package webhooks

import (
	"encoding/json"
	"fmt"
	"net/http"

	admissionv1 "k8s.io/api/admission/v1"
	corev1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/runtime/serializer"
	"k8s.io/apimachinery/pkg/util/jsonmergepatch"
)

func MutatePods(codecs serializer.CodecFactory) func(http.ResponseWriter, *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		var (
			admissionReview   admissionv1.AdmissionReview
			admissionResponse admissionv1.AdmissionResponse
		)

		// decode the request
		if err := json.NewDecoder(r.Body).Decode(&admissionReview); err != nil {
			http.Error(w, fmt.Sprintf("could not decode body: %v", err), http.StatusBadRequest)
			return
		}

		req := admissionReview.Request
		if req == nil {
			http.Error(w, "empty request", http.StatusBadRequest)
			return
		}

		if req.Kind.Kind != "Pod" {
			admissionResponse = admissionv1.AdmissionResponse{
				Allowed: true,
			}
		} else {
			var pod corev1.Pod
			deserializer := codecs.UniversalDeserializer()
			if _, _, err := deserializer.Decode(req.Object.Raw, nil, &pod); err != nil {
				http.Error(w, fmt.Sprintf("could not unmarshal pod: %v", err), http.StatusBadRequest)
				return
			}

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

			// apply mutation
			original, _ := json.Marshal(pod)
			pod.Spec.InitContainers = append(pod.Spec.InitContainers, initContainer)
			modified, _ := json.Marshal(pod)

			patch, err := jsonmergepatch.CreateThreeWayJSONMergePatch(original, modified, original)
			if err != nil {
				http.Error(w, fmt.Sprintf("failed to create patch: %v", err), http.StatusInternalServerError)
				return
			}

			patchType := admissionv1.PatchTypeJSONPatch
			admissionResponse = admissionv1.AdmissionResponse{
				Allowed:   true,
				Patch:     patch,
				PatchType: &patchType,
			}
		}

		admissionReview.Response = &admissionResponse
		admissionReview.Response.UID = admissionReview.Request.UID

		resp, _ := json.Marshal(admissionReview)
		w.Header().Set("Content-Type", "application/json")
		w.Write(resp)
	}
}
