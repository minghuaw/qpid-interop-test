project(qpid-interop-test-fe2o3-amqp-shims-amqp-large-content-test)

cmake_minimum_required(VERSION 3.16.3 FATAL_ERROR)

set(CARGO_BUILD_ROOT ${CMAKE_CURRENT_BINARY_DIR})
set(MAKE_INSTALL_ROOT
    ${CMAKE_INSTALL_PREFIX}/libexec/qpid_interop_test/shims/fe2o3-amqp/amqp_large_content_test)

install(
    CODE "EXECUTE_PROCESS (
        COMMAND cargo install --path ./ --target-dir ${CARGO_BUILD_ROOT} --root ${MAKE_INSTALL_ROOT}
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        )"
)