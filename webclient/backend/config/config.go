package config

import (
	"io/ioutil"
	"path"

	"backend/utils"

	"github.com/pkg/errors"
	"github.com/sirupsen/logrus"
	"gopkg.in/yaml.v2"
)

var clientConfig ClientConfig

type ClientConfig struct {
	DatabaseDialects string `json:"database_dialects" yaml:"database_dialects"`
	DatabaseAddr     string `json:"database_addr" yaml:"database_addr"`
}

func Init(filePath string) {
	// default config
	clientConfig.DatabaseDialects = "sqlite3"
	clientConfig.DatabaseAddr = path.Join(utils.LookUpUserHome(), "pcr_farm.db")

	// read config.yml
	data, err := ioutil.ReadFile(filePath)
	if err != nil {
		logrus.Error(errors.Wrap(err, "read config.yml"))
		return
	}
	if err := yaml.Unmarshal(data, &clientConfig); err != nil {
		logrus.Error(errors.Wrap(err, "yaml.Unmarshal() config.yml"))
		return
	}

	logrus.Infof("load ClientConfig with: %v", clientConfig)
}

func LookUpClientConfig() *ClientConfig {
	return &clientConfig
}
