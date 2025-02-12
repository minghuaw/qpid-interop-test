# Building fe2o3-amqp shim requires
# * cargo
#
# Define -DBUILD_FE2O3_AMQP=ON (or OFF) at the cmake command line
# to force a build or not.

project(qpid-interop-test-fe2o3-amqp-shims)

cmake_minimum_required(VERSION 3.16.3 FATAL_ERROR)

set(build_fe2o3_amqp_default ON)

# Check prerequisites
# 1. Find cargo
find_program(CARGO cargo)
if (CARGO STREQUAL "CARGO-NOTFOUND")
    message(STATUS "cargo not found")
    set(build_fe2o3_amqp_default OFF)
else()
    execute_process(COMMAND cargo --version OUTPUT_VARIABLE ov)
    message(STATUS "cargo is found with version ${ov}")
endif()

# Set option that controls the build process
option(BUILD_FE2O3_AMQP "Build fe2o3-amqp shim" ${build_fe2o3_amqp_default})
message(STATUS "BUILD_FE2O3_AMQP = ${BUILD_FE2O3_AMQP}")

if (BUILD_FE2O3_AMQP)
    add_subdirectory(amqp_types_test)
    add_subdirectory(amqp_large_content_test)
endif()

