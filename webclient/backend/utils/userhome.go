package utils

import (
	"bytes"
	"os"
	"os/exec"
	"os/user"
	"runtime"
	"strings"

	"github.com/pkg/errors"
	"github.com/sirupsen/logrus"
)

// Home returns the home directory for the executing user.
//
// This uses an OS-specific method for discovering the home directory.
// An error is returned if a home directory cannot be detected.
func LookUpUserHome() string {
	u, err := user.Current()
	if err != nil {
		logrus.Error(errors.Wrap(err, "LookUpUserHome user.Current()"))
	} else {
		return u.HomeDir
	}

	// cross compile support

	if "windows" == runtime.GOOS {
		h, err := homeWindows()
		if err != nil {
			logrus.Error(errors.Wrap(err, "LookUpUserHome homeWindows()"))
		} else {
			return h
		}
	}

	// Unix-like system, so just assume Unix
	h, err := homeUnix()
	if err != nil {
		logrus.Error(errors.Wrap(err, "LookUpUserHome homeUnix()"))
	} else {
		return h
	}

	return ""
}

func homeUnix() (string, error) {
	// First prefer the HOME environmental variable
	if home := os.Getenv("HOME"); home != "" {
		return home, nil
	}

	// If that fails, try the shell
	var stdout bytes.Buffer
	cmd := exec.Command("sh", "-c", "eval echo ~$USER")
	cmd.Stdout = &stdout
	if err := cmd.Run(); err != nil {
		return "", err
	}

	result := strings.TrimSpace(stdout.String())
	if result == "" {
		return "", errors.New("blank output when reading home directory")
	}

	return result, nil
}

func homeWindows() (string, error) {
	drive := os.Getenv("HOMEDRIVE")
	path := os.Getenv("HOMEPATH")
	home := drive + path
	if drive == "" || path == "" {
		home = os.Getenv("USERPROFILE")
	}
	if home == "" {
		return "", errors.New("HOMEDRIVE, HOMEPATH, and USERPROFILE are blank")
	}

	return home, nil
}
