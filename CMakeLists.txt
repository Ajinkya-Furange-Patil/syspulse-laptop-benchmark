cmake_minimum_required(VERSION 3.20)
project(SysPulse LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include_directories(include)

find_package(OpenMP REQUIRED)

# Required Windows system libraries for telemetry and hardware detection
set(SYS_LIBS
    Powrprof
    wbemuuid
    ole32
    oleaut32
    Advapi32
)

# Optional CUDA support detection
include(CheckLanguage)
check_language(CUDA)

if(CMAKE_CUDA_COMPILER)
    enable_language(CUDA)
    set(CMAKE_CUDA_STANDARD 20)
    set(CMAKE_CUDA_STANDARD_REQUIRED ON)
    message(STATUS "[SysPulse] CUDA Compiler detected: ${CMAKE_CUDA_COMPILER}")
    add_executable(laptop_benchmark
        src/main.cpp
        src/cuda_kernels.cu
    )
    target_compile_definitions(laptop_benchmark PRIVATE _CRT_SECURE_NO_WARNINGS)
    target_link_libraries(laptop_benchmark PRIVATE OpenMP::OpenMP_CXX ${SYS_LIBS})
else()
    message(STATUS "[SysPulse] CUDA compiler not detected - building in Universal CPU mode with stub")
    add_executable(laptop_benchmark
        src/main.cpp
        src/cuda_stub.cpp
    )
    target_compile_definitions(laptop_benchmark PRIVATE _CRT_SECURE_NO_WARNINGS)
    target_link_libraries(laptop_benchmark PRIVATE OpenMP::OpenMP_CXX ${SYS_LIBS})
endif()

# Set output executable location to bin/
set_target_properties(laptop_benchmark PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/bin"
)
