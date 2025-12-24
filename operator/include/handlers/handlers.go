package handlers

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/amirhnajafiz/flap/include/handlers/hooks"
	"github.com/amirhnajafiz/flap/pkg/admission"

	"github.com/sirupsen/logrus"
	"k8s.io/apimachinery/pkg/runtime/serializer"
)

// Health returns 200 when things are good.
func Health(w http.ResponseWriter, r *http.Request) {
	logrus.WithField("uri", r.RequestURI).Debug("healthy")
	fmt.Fprint(w, "OK")
}

// MutateCreatePod mutates pods that are created.
func MutateCreatePod(codecs serializer.CodecFactory) func(http.ResponseWriter, *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		// init a new logger instance with request uri
		logger := logrus.WithField("uri", r.RequestURI)
		logger.Debug("received mutation request")

		// extract the admission request
		in, err := parseRequest(*r)
		if err != nil {
			logger.Error(err)
			http.Error(w, err.Error(), http.StatusBadRequest)
			return
		}

		// create a new admitter
		adm := admission.Admitter{
			Codecs:  codecs,
			Logger:  logger,
			Request: in.Request,
		}

		// call the hook and store it in a review var
		review := hooks.HookOnPodCreate(&adm)

		// return the admission review response
		resp, err := json.Marshal(review)
		if err != nil {
			logger.Error(err)
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		logger.Debug("replied mutation response")

		w.Header().Set("Content-Type", "application/json")
		w.Write(resp)
	}
}

// MutateDeletePod mutates pods that are deleted.
func MutateDeletePod(codecs serializer.CodecFactory) func(http.ResponseWriter, *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		// init a new logger instance with request uri
		logger := logrus.WithField("uri", r.RequestURI)
		logger.Debug("received mutation request")

		// extract the admission request
		in, err := parseRequest(*r)
		if err != nil {
			logger.Error(err)
			http.Error(w, err.Error(), http.StatusBadRequest)
			return
		}

		// create a new admitter
		adm := admission.Admitter{
			Codecs:  codecs,
			Logger:  logger,
			Request: in.Request,
		}

		// return the admission review response
		resp, err := json.Marshal(adm)
		if err != nil {
			logger.Error(err)
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		logger.Debug("replied mutation response")

		w.Header().Set("Content-Type", "application/json")
		w.Write(resp)
	}
}
