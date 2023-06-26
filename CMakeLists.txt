cmake_minimum_required(VERSION 3.16)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(PICO_SDK_PATH           /home/mahdif/projects/gh/pico/pico-sdk/)
set(FREERTOS_KERNEL_PATH    /home/mahdif/projects/gh/pico/FreeRTOS-Kernel)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
include(./pico_sdk_import.cmake)
include(./FreeRTOS_Kernel_import.cmake)

project(demo C CXX ASM)

pico_sdk_init()

add_executable(${PROJECT_NAME}
    src/main.c
    src/main_full.c
    src/IntQueueTimer.c
    src/RegTest.s
    src/blocktim.c
    src/countsem.c
    src/dynamic.c
    src/recmutex.c
    src/QueueOverwrite.c
    src/EventGroupsDemo.c
    src/IntSemTest.c
    src/IntQueue.c
    src/TaskNotify.c
    src/TimerDemo.c
    src/GenQTest.c
    src/death.c
    src/semtest.c
    src/BlockQ.c
    src/flop.c
)

target_include_directories(${PROJECT_NAME} PRIVATE
    ./include
)

target_compile_definitions(${PROJECT_NAME} PRIVATE mainCREATE_SIMPLE_BLINKY_DEMO_ONLY=0)
target_compile_definitions(${PROJECT_NAME} PRIVATE PICO_STDIO_STACK_BUFFER_SIZE=64)

target_link_libraries(${PROJECT_NAME} pico_stdlib FreeRTOS-Kernel FreeRTOS-Kernel-Heap4)

pico_enable_stdio_usb(${PROJECT_NAME} 1)
pico_enable_stdio_uart(${PROJECT_NAME} 0)
pico_add_extra_outputs(${PROJECT_NAME})
