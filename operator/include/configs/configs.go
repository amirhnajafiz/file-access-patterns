package configs

import (
	"log"
	"strings"

	"github.com/spf13/viper"
)

// Config hold the operator tune parameters.
// all configuration parameters must be set as environment variables or as a `.env` file.
type Config struct {
	LogLevel string `mapstructure:"log_level"`
	JSONLog  bool   `mapstructure:"json_log"`
	TLS      struct {
		Enable   bool   `mapstructure:"enable"`
		CertPath string `mapstructure:"cert_path"`
		KeyPath  string `mapstructure:"key_path"`
	} `mapstructure:"tls"`
}

// LoadConfigs reads the env variables into a Config struct.
func LoadConfigs() (*Config, error) {
	v := viper.New()

	// read from `.env`
	v.SetConfigFile(".env")
	v.AddConfigPath(".")

	// bind env variables automatically
	v.AutomaticEnv()

	// set prefix
	v.SetEnvPrefix("flap")
	v.SetEnvKeyReplacer(strings.NewReplacer(".", "__"))

	// read configs
	if err := v.ReadInConfig(); err != nil {
		log.Printf("failed to read config file: %v\n", err)
	}

	var cfg Config
	if err := v.Unmarshal(&cfg); err != nil {
		return nil, err
	}

	return &cfg, nil
}
