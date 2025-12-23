package main

import (
	"fmt"
	"net/http"

	"github.com/amirhnajafiz/flap/include/cmd"
	"github.com/amirhnajafiz/flap/include/configs"
	"github.com/amirhnajafiz/flap/include/handlers"
	"github.com/amirhnajafiz/flap/include/telemetry/logging"
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
	// read configs
	cfg, err := configs.LoadConfigs()
	if err != nil {
		panic(
			fmt.Sprintf("failed to load configs: %v", err),
		)
	}

	// set logrus logging
	logging.SetLogger(cfg.LogLevel, cfg.JSONLog)

	// register http handlers
	http.HandleFunc("/health", handlers.ServeHealth)
	http.HandleFunc("/mutate", webhooks.MutatePods(codecs))

	// listens to clear text http unless TLS env var is set to "true"
	if cfg.TLS {
		cmd.ServeHTTPS()
	} else {
		cmd.ServeHTTP()
	}
}
