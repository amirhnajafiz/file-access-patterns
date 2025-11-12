package cmd

import (
	"net/http"

	"github.com/sirupsen/logrus"
)

// ServeHTTPS on port 443.
func ServeHTTPS() {
	cert := "/etc/flap/tls/tls.crt"
	key := "/etc/flap/tls/tls.key"
	logrus.Print("Listening on port 443...")
	logrus.Fatal(http.ListenAndServeTLS(":443", cert, key, nil))
}

// ServeHTTP on port 8080.
func ServeHTTP() {
	logrus.Print("Listening on port 8080...")
	logrus.Fatal(http.ListenAndServe(":8080", nil))
}
