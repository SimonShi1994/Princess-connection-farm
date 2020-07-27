package apps

import (
	"github.com/pkg/errors"
	"github.com/sirupsen/logrus"
)

func RunServer(listenAddr string) {
	r := LookUpRouter()
	err := r.Run(listenAddr)
	if err != nil {
		logrus.Fatal(errors.Wrap(err, "webclient runserver"))
	}
}
