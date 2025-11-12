package configs

import (
	"strings"

	"github.com/spf13/viper"
)

const (
	envPrefix = "FLAP_"
)

// Config hold the operator tune parameters.
type Config struct {
	LogLevel string `mapstructure:"LOG_LEVEL"`
	JSONLog  bool   `mapstructure:"JSON_LOG"`
}

// LoadConfigs reads the env variables into a Config struct.
func LoadConfigs() (*Config, error) {
	viper.SetEnvPrefix(envPrefix)
	viper.AutomaticEnv()
	viper.SetEnvKeyReplacer(strings.NewReplacer(".", "_"))

	var cfg Config
	if err := viper.Unmarshal(&cfg); err != nil {
		return nil, err
	}

	return &cfg, nil
}
