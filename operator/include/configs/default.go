package configs

// Default returns a default config instance.
func Default() Config {
	var cfg Config

	cfg.LogLevel = "info"
	cfg.JSONLog = false
	cfg.TLS.Enable = false

	return cfg
}
