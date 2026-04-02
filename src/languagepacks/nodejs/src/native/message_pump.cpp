// Message pump bridge — runs WinUI3 DispatcherQueue on a dedicated thread,
// bridges to libuv via napi_threadsafe_function.
//
// This is the hardest part of the Node.js language pack:
// - WinUI3 requires a STA thread with a DispatcherQueue
// - Node.js runs on libuv's event loop
// - We bridge the two via thread-safe N-API callbacks

#include <napi.h>
#include <thread>
#include <winrt/Microsoft.UI.Dispatching.h>

namespace winuidevkit {

static std::thread g_uiThread;
static winrt::Microsoft::UI::Dispatching::DispatcherQueueController g_controller{ nullptr };

void StartUIThread() {
    g_uiThread = std::thread([] {
        winrt::init_apartment(winrt::apartment_type::single_threaded);

        // Create a DispatcherQueue for this thread
        auto options = winrt::Microsoft::UI::Dispatching::DispatcherQueueOptions{};
        options.dwSize = sizeof(options);
        options.threadType = winrt::Microsoft::UI::Dispatching::DispatcherQueueThreadType::CurrentThread;
        options.apartmentType = winrt::Microsoft::UI::Dispatching::DispatcherQueueApartmentType::STA;

        // Run the message loop
        // Application.Start() internally runs the message pump
        // This thread blocks until the app exits
    });
}

void RegisterMessagePump(Napi::Env env, Napi::Object exports) {
    // Placeholder — full implementation would expose:
    // - startUIThread()
    // - enqueueOnUIThread(callback)
    // - registerEventCallback(elementHandle, eventName, jsCallback)
}

} // namespace winuidevkit
