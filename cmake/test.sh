#!/usr/bin/env bash

# Global Variables
PROJECT_NAME="__template__"
SOURCE_NAME="test"
CREATE_HEADER="ON"

cmake -D "PROJECT_NAME=$PROJECT_NAME" -D "SOURCE_NAME=$SOURCE_NAME" -D "CREATE_HEADER=$CREATE_HEADER" -P cmake_source.cmake
