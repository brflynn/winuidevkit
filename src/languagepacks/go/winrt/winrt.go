// Package winrt provides minimal WinRT interop for Go.
//
// This is a NEW projection — go-ole only covers COM IUnknown/IDispatch,
// but WinUI3 requires WinRT (IInspectable) activation and HSTRING support.
//
// Only the types needed for WinUI3 XAML apps are projected here.
package winrt

import (
	"syscall"
	"unsafe"
)

var (
	modcombase = syscall.NewLazyDLL("combase.dll")

	procRoInitialize           = modcombase.NewProc("RoInitialize")
	procRoUninitialize         = modcombase.NewProc("RoUninitialize")
	procRoActivateInstance     = modcombase.NewProc("RoActivateInstance")
	procRoGetActivationFactory = modcombase.NewProc("RoGetActivationFactory")
	procWindowsCreateString    = modcombase.NewProc("WindowsCreateString")
	procWindowsDeleteString    = modcombase.NewProc("WindowsDeleteString")
	procWindowsGetStringRawBuffer = modcombase.NewProc("WindowsGetStringRawBuffer")
)

// HSTRING wraps a WinRT string handle.
type HSTRING uintptr

// NewHSTRING creates a WinRT HSTRING from a Go string.
func NewHSTRING(s string) (HSTRING, error) {
	u16 := syscall.StringToUTF16(s)
	var hs HSTRING
	hr, _, _ := procWindowsCreateString.Call(
		uintptr(unsafe.Pointer(&u16[0])),
		uintptr(len(u16)-1), // exclude null terminator
		uintptr(unsafe.Pointer(&hs)),
	)
	if hr != 0 {
		return 0, NewHRESULT(hr)
	}
	return hs, nil
}

// Delete releases the HSTRING.
func (hs HSTRING) Delete() {
	if hs != 0 {
		procWindowsDeleteString.Call(uintptr(hs))
	}
}

// String converts the HSTRING back to a Go string.
func (hs HSTRING) String() string {
	if hs == 0 {
		return ""
	}
	var length uint32
	buf, _, _ := procWindowsGetStringRawBuffer.Call(uintptr(hs), uintptr(unsafe.Pointer(&length)))
	if buf == 0 {
		return ""
	}
	u16 := unsafe.Slice((*uint16)(unsafe.Pointer(buf)), length)
	return syscall.UTF16ToString(u16)
}

// IInspectable represents the WinRT IInspectable interface.
// This extends IUnknown with GetIids, GetRuntimeClassName, GetTrustLevel.
type IInspectable struct {
	VTable *IInspectableVtbl
}

// IInspectableVtbl is the vtable for IInspectable.
type IInspectableVtbl struct {
	// IUnknown
	QueryInterface uintptr
	AddRef         uintptr
	Release        uintptr
	// IInspectable
	GetIids            uintptr
	GetRuntimeClassName uintptr
	GetTrustLevel      uintptr
}

// HRESULT wraps a COM error code.
type HRESULT struct {
	Code uintptr
}

func NewHRESULT(code uintptr) HRESULT {
	return HRESULT{Code: code}
}

func (hr HRESULT) Error() string {
	return syscall.Errno(hr.Code).Error()
}

// Initialize calls RoInitialize(RO_INIT_MULTITHREADED).
func Initialize() error {
	const roInitMultiThreaded = 1
	hr, _, _ := procRoInitialize.Call(roInitMultiThreaded)
	if hr != 0 {
		return NewHRESULT(hr)
	}
	return nil
}

// Uninitialize calls RoUninitialize.
func Uninitialize() {
	procRoUninitialize.Call()
}

// ActivateInstance activates a WinRT class by its runtime class name.
func ActivateInstance(className string) (unsafe.Pointer, error) {
	hs, err := NewHSTRING(className)
	if err != nil {
		return nil, err
	}
	defer hs.Delete()

	var instance unsafe.Pointer
	hr, _, _ := procRoActivateInstance.Call(
		uintptr(hs),
		uintptr(unsafe.Pointer(&instance)),
	)
	if hr != 0 {
		return nil, NewHRESULT(hr)
	}
	return instance, nil
}
