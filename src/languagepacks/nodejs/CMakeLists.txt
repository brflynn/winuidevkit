cmake_minimum_required(VERSION 3.20)
project(winuidevkit_native)

# Use C++/WinRT for WinUI3 access
set(CMAKE_CXX_STANDARD 20)

# Find Node.js N-API headers
include_directories(${CMAKE_JS_INC})

# Windows App SDK headers (from NuGet or local cache)
# Set WINAPPSDK_DIR to the extracted NuGet package path
if(NOT DEFINED WINAPPSDK_DIR)
    set(WINAPPSDK_DIR "$ENV{LOCALAPPDATA}/WinUIDevKit/sdk/include")
endif()

add_library(${PROJECT_NAME} SHARED
    src/native/bootstrap.cpp
    src/native/xaml_loader.cpp
    src/native/binder.cpp
    src/native/message_pump.cpp
    src/native/addon.cpp
)

target_include_directories(${PROJECT_NAME} PRIVATE
    ${CMAKE_JS_INC}
    ${WINAPPSDK_DIR}
)

target_link_libraries(${PROJECT_NAME}
    ${CMAKE_JS_LIB}
    windowsapp.lib
)

set_target_properties(${PROJECT_NAME} PROPERTIES
    PREFIX ""
    SUFFIX ".node"
)
