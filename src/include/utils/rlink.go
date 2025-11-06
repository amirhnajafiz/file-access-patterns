package utils

// file: src/include/utils/rlink.go

import (
	"os/exec"
	"strings"
	"sync"
)

// RLink runs the utils/rlink.sh script to get the filename from a pid and fd.
func RLink(pid, fd string, cache *sync.Map) string {
	key := pid + "," + fd
	if val, ok := cache.Load(key); ok {
		return val.(string)
	}

	// run the command: sudo ./utils/rlink.sh pid fd
	cmd := exec.Command("sudo", "./utils/rlink.sh", pid, fd)
	out, err := cmd.Output()
	var file string

	if err != nil {
		file = pid + "::" + fd
	} else {
		file = strings.TrimSpace(string(out))
	}

	cache.Store(key, file)

	return file
}
