package webhooks

import (
	"encoding/json"
	"net/http"

	"github.com/amirhnajafiz/flap/pkg/admission"
	"github.com/sirupsen/logrus"

	"k8s.io/apimachinery/pkg/runtime/serializer"
)

func MutatePods(codecs serializer.CodecFactory) func(http.ResponseWriter, *http.Request) {
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

		// call reconcile to get the admission review by passing the admitter
		admissionReview := reconcile(&adm)

		// return the admission review response
		resp, err := json.Marshal(admissionReview)
		if err != nil {
			logger.Error(err)
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		w.Write(resp)
	}
}
