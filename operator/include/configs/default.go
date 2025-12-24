package configs

import "github.com/spf13/viper"

// Default returns a default viper instance.
func Default() *viper.Viper {
	v := viper.New()

	v.SetDefault("log_level", "info")
	v.SetDefault("json_log", false)
	v.SetDefault("tls.enable", false)
	v.SetDefault("tls.cert_path", "/etc/flap/tls/tls.crt")
	v.SetDefault("tls.key_path", "/etc/flap/tls/tls.key")

	return v
}
