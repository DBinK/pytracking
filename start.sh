#!/bin/bash# 

#获取脚本所在目录的方法
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
echo "脚本所在目录: $SCRIPT_DIR"

cd "$SCRIPT_DIR"
uv run ./interfaces/pytracking_server.py