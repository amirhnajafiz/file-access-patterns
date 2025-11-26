package handlers

import (
	"fmt"
	"net/http"

	"github.com/sirupsen/logrus"
)

// ServeHealth returns 200 when things are good.
func ServeHealth(w http.ResponseWriter, r *http.Request) {
	logrus.WithField("uri", r.RequestURI).Debug("healthy")
	fmt.Fprint(w, "OK")
}
