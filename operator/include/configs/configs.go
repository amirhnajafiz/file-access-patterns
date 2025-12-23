package configs

import (
	"fmt"
	"reflect"
	"strings"

	"github.com/spf13/viper"
)

// Config hold the operator tune parameters.
// all configuration parameters must be set as environment variables or as a `.env` file.
type Config struct {
	LogLevel string `mapstructure:"flap.log_level" env:"FLAP_LOG_LEVEL"`
	JSONLog  bool   `mapstructure:"flap.json_log"  env:"FLAP_JSON_LOG"`
	TLS      bool   `mapstructure:"flap.tls"       env:"FLAP_TLS"`
}

func bindEnvs(v *viper.Viper, iface interface{}) error {
	val := reflect.ValueOf(iface)
	if val.Kind() != reflect.Ptr {
		return fmt.Errorf("bindEnvs expects a pointer")
	}

	val = val.Elem()
	typ := val.Type()

	for i := 0; i < val.NumField(); i++ {
		field := typ.Field(i)

		key := field.Tag.Get("mapstructure")
		env := field.Tag.Get("env")

		if key == "" || env == "" {
			continue
		}

		if err := v.BindEnv(key, env); err != nil {
			return err
		}
	}

	return nil
}

// LoadConfigs reads the env variables into a Config struct.
func LoadConfigs() (*Config, error) {
	v := viper.New()

	v.SetEnvKeyReplacer(strings.NewReplacer(".", "_"))
	v.AutomaticEnv()

	v.SetConfigFile(".env")
	_ = v.ReadInConfig()

	var cfg Config

	if err := bindEnvs(v, &cfg); err != nil {
		return nil, err
	}

	if err := v.Unmarshal(&cfg); err != nil {
		return nil, err
	}

	return &cfg, nil
}
