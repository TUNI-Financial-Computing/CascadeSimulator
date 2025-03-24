cmake_minimum_required(VERSION 3.15)
project(${SKBUILD_PROJECT_NAME} LANGUAGES CXX)

set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 CONFIG REQUIRED)

pybind11_add_module(_cascade_generator MODULE src/main.cpp)
install(TARGETS _cascade_generator DESTINATION ${SKBUILD_PROJECT_NAME})
