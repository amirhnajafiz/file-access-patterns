package worker

// file: src/include/worker/worker.go

import (
	"fmt"
	"regexp"
	"strings"
	"sync"

	"github.com/amirhnajafiz/file-access-patterns/src/include/utils"
)

type Packed struct {
	In  string
	Out string
}

// Worker starts a process that gets the input lines as jobs and processes them based on its cases.
func Worker(jobs <-chan string, results chan<- Packed, cache *sync.Map, wg *sync.WaitGroup) {
	defer wg.Done()

	// filter @ lines
	opRegex := regexp.MustCompile(`^@([a-zA-Z0-9_]+)\[`)

	// un_op and op cases
	unRegex := regexp.MustCompile(`^@([a-zA-Z0-9_]+)\[([0-9]+),\s*([0-9]+)\]:\s*(.*)$`)

	// listern on the input channel for incomming lines from the main go-routine
	for line := range jobs {
		p := Packed{In: line, Out: line}
		if !strings.HasPrefix(line, "@") {
			results <- p
			continue
		}

		// match the operations (un_op or op)
		opMatch := opRegex.FindStringSubmatch(line)
		if opMatch == nil {
			continue
		}

		op := opMatch[1]

		// un lines
		if strings.HasPrefix(op, "un") {
			m := unRegex.FindStringSubmatch(line)
			if m == nil {
				results <- p
				continue
			}

			pid := m[2]
			fd := m[3]
			value := m[4]

			// get the filename by running the utils/rlink
			file := utils.RLink(pid, fd, cache)

			p.Out = fmt.Sprintf("@%s[%s]: %s", strings.TrimPrefix(op, "un_"), file, value)
			results <- p
		} else {
			// fallback print raw line
			results <- p
		}
	}
}
