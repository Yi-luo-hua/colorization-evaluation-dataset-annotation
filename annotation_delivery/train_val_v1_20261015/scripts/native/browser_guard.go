// Build on Windows: go build -o ../no_browser/rundll32.exe browser_guard.go
// agy's Windows OAuth opener runs rundll32 url.dll,FileProtocolHandler URL.
package main

import (
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"
)

func main() {
	if len(os.Args) > 1 && strings.EqualFold(os.Args[1], "url.dll,FileProtocolHandler") {
		marker := os.Getenv("MCL_AUTH_BROWSER_BLOCK_LOG")
		if marker != "" {
			data, _ := json.Marshal(map[string]any{
				"reason": "auth_browser_blocked", "blocked_at": time.Now().UTC().Format(time.RFC3339Nano),
				"pid": os.Getpid(), "parent_pid": os.Getppid(),
			})
			if err := os.WriteFile(marker, data, 0600); err != nil {
				fmt.Fprintln(os.Stderr, err)
			}
		}
		fmt.Fprintln(os.Stderr, "auth_browser_blocked: background jobs cannot open browser login")
		os.Exit(77)
	}
	// Preserve other rundll32 uses in this child environment.
	cmd := exec.Command(filepath.Join(os.Getenv("SystemRoot"), "System32", "rundll32.exe"), os.Args[1:]...)
	cmd.Stdin, cmd.Stdout, cmd.Stderr = os.Stdin, os.Stdout, os.Stderr
	if err := cmd.Run(); err != nil {
		if exit, ok := err.(*exec.ExitError); ok {
			os.Exit(exit.ExitCode())
		}
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
