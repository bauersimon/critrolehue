package config

import (
	"os"

	"github.com/knadh/koanf/parsers/json"
	"github.com/knadh/koanf/providers/file"
	"github.com/knadh/koanf/v2"
)

var Global = koanf.New(".")
var configPath string

func Init(path string) error {
	configPath = path
	if _, err := os.Stat(path); os.IsNotExist(err) {
		return Save()
	}

	return Global.Load(file.Provider(path), json.Parser())
}

func Save() error {
	data, err := Global.Marshal(json.Parser())
	if err != nil {
		return err
	}
	if err := os.WriteFile(configPath, data, 0644); err != nil {
		return err
	}

	return nil
}
