package database

import (
	"sync"

	"backend/config"

	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/sqlite"
	"github.com/pkg/errors"
	"github.com/sirupsen/logrus"
)

var mutex sync.Mutex
var instance *gorm.DB

func LookUpDB() *gorm.DB {
	return instance
}

func Init() {
	mutex.Lock()
	defer mutex.Unlock()

	c := config.LookUpClientConfig()
	db, err := gorm.Open(c.DatabaseDialects, c.DatabaseAddr)
	if err != nil {
		logrus.Error(errors.Wrap(err, "gorm open"))
		return
	}
	db.LogMode(true)

	//db.DB().SetMaxIdleConns(config.DBConfig.MaxIdleConns)
	//db.DB().SetMaxOpenConns(config.DBConfig.MaxOpenConns)

	db.SingularTable(true)
	//db.DB().SetConnMaxLifetime(config.DBConfig.ConnMaxLifetime)
	instance = db
}
