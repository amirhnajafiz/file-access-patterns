package main

import (
	"fmt"
	"net/http"

	"github.com/amirhnajafiz/flap/include/cmd"
	"github.com/amirhnajafiz/flap/include/configs"
	"github.com/amirhnajafiz/flap/include/handlers"
	"github.com/amirhnajafiz/flap/include/telemetry/logging"

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
	http.HandleFunc("/health", handlers.Health)
	http.HandleFunc("/mutate/crt", handlers.MutatePod(codecs, "create_pod"))
	http.HandleFunc("/mutate/del", handlers.MutatePod(codecs, "delete_pod"))

	// listens to clear text http unless TLS env var is set to "true"
	if cfg.TLS.Enable {
		cmd.ServeHTTPS(cfg.TLS.CertPath, cfg.TLS.KeyPath)
	} else {
		cmd.ServeHTTP()
	}
}
