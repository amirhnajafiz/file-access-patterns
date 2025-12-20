package configs

import (
	"strings"

	"github.com/spf13/viper"
)

// Config hold the operator tune parameters.
// all configuration parameters must be set as environment variables or as a `.env` file.
type Config struct {
	LogLevel string `mapstructure:"FLAP_LOG_LEVEL"`
	JSONLog  bool   `mapstructure:"FLAP_JSON_LOG"`
	TLS      bool   `mapstructure:"FLAP_TLS"`
}

// LoadConfigs reads the env variables into a Config struct.
func LoadConfigs() (*Config, error) {
	viper.SetConfigFile(".env")
	_ = viper.ReadInConfig() // ignore if .env missing

	viper.AutomaticEnv()
	viper.SetEnvKeyReplacer(strings.NewReplacer(".", "_"))

	viper.BindEnv("FLAP_LOG_LEVEL")
	viper.BindEnv("FLAP_JSON_LOG")
	viper.BindEnv("FLAP_TLS")

	var cfg Config
	if err := viper.Unmarshal(&cfg); err != nil {
		return nil, err
	}

	return &cfg, nil
}
