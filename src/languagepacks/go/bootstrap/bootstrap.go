// Package bootstrap initializes the Windows App Runtime via DDLM.
package bootstrap

import (
	"fmt"
	"syscall"
)

var (
	modBootstrap = syscall.NewLazyDLL("Microsoft.WindowsAppRuntime.Bootstrap.dll")

	procMddBootstrapInitialize2 = modBootstrap.NewProc("MddBootstrapInitialize2")
	procMddBootstrapShutdown    = modBootstrap.NewProc("MddBootstrapShutdown")
)

const (
	sdkVersionMajorMinor uint32 = 0x00010008 // SDK 1.8
)

// Initialize loads the Windows App Runtime via the DDLM bootstrap.
func Initialize() error {
	hr, _, _ := procMddBootstrapInitialize2.Call(
		uintptr(sdkVersionMajorMinor),
		0, // versionTag (none)
		0, // minVersion (any)
		0, // options (default)
	)
	if hr != 0 {
		return fmt.Errorf("MddBootstrapInitialize2 failed: HRESULT 0x%08x", hr)
	}
	return nil
}

// Shutdown releases the bootstrap.
func Shutdown() {
	procMddBootstrapShutdown.Call()
}
