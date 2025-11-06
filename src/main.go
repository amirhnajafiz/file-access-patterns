package main

// file main.go

import (
	"bufio"
	"fmt"
	"os"
	"os/exec"
	"sync"

	"github.com/amirhnajafiz/file-access-patterns/src/include/worker"
)

func main() {
	// check the input size
	if len(os.Args) < 2 {
		fmt.Fprintf(os.Stderr, "Usage: %s <command> [args...]\n", os.Args[0])
		os.Exit(1)
	}

	// create jobs as input channel, results as output channel, and cache for rlink caching
	jobs := make(chan string, 100)
	results := make(chan string, 100)
	cache := &sync.Map{}

	// wait group for workers
	var wg sync.WaitGroup
	numWorkers := 10

	// start the workers
	for i := 0; i < numWorkers; i++ {
		wg.Add(1)
		go worker.Worker(jobs, results, cache, &wg)
	}

	// run the command
	cmd := exec.Command(os.Args[1], os.Args[2:]...)
	stdout, err := cmd.StdoutPipe()
	if err != nil {
		fmt.Fprintf(os.Stderr, "error getting stdout pipe: %v\n", err)
		os.Exit(1)
	}

	if err := cmd.Start(); err != nil {
		fmt.Fprintf(os.Stderr, "error starting command: %v\n", err)
		os.Exit(1)
	}

	// feed lines to jobs channel
	scanner := bufio.NewScanner(stdout)
	go func() {
		for scanner.Scan() {
			jobs <- scanner.Text()
		}
		close(jobs)
	}()

	// wait for all workers to finish then close results
	go func() {
		wg.Wait()
		close(results)
	}()

	// collect and print results
	for res := range results {
		fmt.Println(res)
	}

	// wait for the command
	if err := cmd.Wait(); err != nil {
		fmt.Fprintf(os.Stderr, "command error: %v\n", err)
		os.Exit(1)
	}
}
