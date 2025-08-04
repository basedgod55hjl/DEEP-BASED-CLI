#!/bin/bash
# cleanup_and_restructure.sh

# Define base directories
BASE_DIR="DEEP-CLI"
SRC_DIR="${BASE_DIR}/src"
TOOLS_DIR="${SRC_DIR}/tools"
CORE_DIR="${SRC_DIR}/core"
UTILS_DIR="${SRC_DIR}/utils"

# Create clean directory structure
mkdir -p ${CORE_DIR}
mkdir -p ${TOOLS_DIR}
mkdir -p ${UTILS_DIR}
mkdir -p ${BASE_DIR}/config
mkdir -p ${BASE_DIR}/plugins
mkdir -p ${BASE_DIR}/data/models
mkdir -p ${BASE_DIR}/logs

# Remove redundant files and directories
find ${BASE_DIR} -type f \( \
    -name "*.test.*" \
    -o -name "demo*.py" \
    -o -name "test_*.py" \
    -o -name "sample*.py" \
    -o -name "*_demo.py" \
\) -delete

# Remove empty directories
find ${BASE_DIR} -type d -empty -delete

echo "Project restructured successfully!" 