package main

import (
	"fmt"
	"log"
	"net/http"

	"github.com/amirhnajafiz/flap/include/webhooks"
	corev1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/runtime/serializer"
)

var (
	scheme = runtime.NewScheme()
	codecs = serializer.NewCodecFactory(scheme)
)

func init() {
	_ = corev1.AddToScheme(scheme)
}

func main() {
	http.HandleFunc("/mutate", webhooks.MutatePods(codecs))

	addr := ":8443"
	fmt.Printf("Starting webhook server on %s...\n", addr)

	// Normally you serve with TLS, but for local dev we can skip
	if err := http.ListenAndServeTLS(addr, "/tls/tls.crt", "/tls/tls.key", nil); err != nil {
		log.Fatalf("server failed: %v", err)
	}
}
