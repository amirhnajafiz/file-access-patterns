package cmd

import (
	"net/http"

	"github.com/sirupsen/logrus"
)

// ServeHTTPS start a server on port 443.
// tls files must exist in `/etc/flap/tls`, otherwise the program panics.
func ServeHTTPS() {
	cert := "/etc/flap/tls/tls.crt"
	key := "/etc/flap/tls/tls.key"
	logrus.Print("Listening on port 443...")
	logrus.Fatal(http.ListenAndServeTLS(":443", cert, key, nil))
}

// ServeHTTP on port 8080.
// not need for any tls files, but Kubernetes integration might fail on http.
func ServeHTTP() {
	logrus.Print("Listening on port 8080...")
	logrus.Fatal(http.ListenAndServe(":8080", nil))
}
