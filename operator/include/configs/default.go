package configs

import "github.com/spf13/viper"

// Default returns a default viper instance.
func Default() *viper.Viper {
	v := viper.New()

	v.SetDefault("log_level", "info")
	v.SetDefault("json_log", false)
	v.SetDefault("tls.enable", false)

	return v
}
