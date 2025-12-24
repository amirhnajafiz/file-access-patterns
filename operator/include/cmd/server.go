package cmd

import (
	"net/http"

	"github.com/sirupsen/logrus"
)

// ServeHTTPS start a server on port 443.
func ServeHTTPS(cert, key string) {
	logrus.Print("Listening on port 443...")
	logrus.Fatal(http.ListenAndServeTLS(":443", cert, key, nil))
}

// ServeHTTP on port 8080.
// not need for any tls files, but Kubernetes integration might fail on http.
func ServeHTTP() {
	logrus.Print("Listening on port 8080...")
	logrus.Fatal(http.ListenAndServe(":8080", nil))
}
