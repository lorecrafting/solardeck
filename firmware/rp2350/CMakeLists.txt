cmake_minimum_required(VERSION 3.13)

project(solardeck_rp2350 C CXX ASM)
set(CMAKE_C_STANDARD 11)

# Check if Pico SDK is provided
if (DEFINED ENV{PICO_SDK_PATH})
    include($ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake)
    pico_sdk_init()

    add_executable(solardeck_rp2350
        src/main.c
        src/solardeck_sm.c
    )
    target_compile_definitions(solardeck_rp2350 PRIVATE PICO_SDK_AVAILABLE=1)
    target_include_directories(solardeck_rp2350 PRIVATE include)
    target_link_libraries(solardeck_rp2350 pico_stdlib hardware_gpio hardware_adc hardware_uart)
    pico_add_extra_outputs(solardeck_rp2350)
endif()

# Native Host Test Executable
add_executable(test_rp2350_sm
    test/test_rp2350_sm.c
    src/solardeck_sm.c
)
target_include_directories(test_rp2350_sm PRIVATE include)

add_executable(test_regs test/test_regs.c)
target_include_directories(test_regs PRIVATE include)

enable_testing()
add_test(NAME test_rp2350_sm COMMAND test_rp2350_sm)
add_test(NAME test_regs COMMAND test_regs)
