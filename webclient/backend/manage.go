package main

import (
	"flag"

	"backend/apps"
	"backend/config"
	"backend/database"
	"backend/logger"
)

var migrate bool
var runserver bool
var listen string
var configPath string

func init() {
	flag.BoolVar(&migrate, "m", false, "use to migrate")
	flag.BoolVar(&runserver, "r", false, "use to runserver")
	flag.StringVar(&listen, "l", "localhost:8080", "use to set http server listen address")
	flag.StringVar(&configPath, "c", "config.yml", "use to set config.yml path")
	flag.Parse()
	if !migrate && !runserver {
		flag.Usage() // echo help text
	}

	logger.Init()
	config.Init(configPath)
	database.Init()
}

func main() {
	if migrate {
		database.Migrate()
	}
	if runserver {
		apps.RunServer("localhost:8080")
	}
}
