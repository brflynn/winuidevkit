// Go HelloWorld — uses go-ole + WinUIDevKit's WinRT projection.
package main

import (
	"fmt"
	"os"

	"github.com/brflynn/WinUIDevKit/src/languagepacks/go/bootstrap"
	"github.com/brflynn/WinUIDevKit/src/languagepacks/go/winrt"
)

func main() {
	// Initialize WinRT + WinAppSDK
	if err := winrt.Initialize(); err != nil {
		fmt.Fprintf(os.Stderr, "RoInitialize failed: %v\n", err)
		os.Exit(1)
	}

	if err := bootstrap.Initialize(); err != nil {
		fmt.Fprintf(os.Stderr, "Bootstrap failed: %v\n", err)
		os.Exit(1)
	}
	defer bootstrap.Shutdown()

	// Read XAML
	xamlBytes, err := os.ReadFile("app/MainWindow.xaml")
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to read XAML: %v\n", err)
		os.Exit(1)
	}

	// Load via XamlReader (using WinRT activation)
	xamlStr := string(xamlBytes)
	fmt.Printf("Loaded XAML (%d bytes)\n", len(xamlStr))

	// In full implementation:
	// 1. RoActivateInstance("Microsoft.UI.Xaml.Markup.XamlReader")
	// 2. Call Load(xamlStr) via vtable
	// 3. Create Window, set Content, Activate

	fmt.Println("Hello from WinUI3 + Go!")
}
