#!/bin/bash
# 簡化的 GPU 數據收集腳本
# 使用重構後的 src/simple_collector.py

# 獲取腳本目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 設置環境
cd "$SCRIPT_DIR"

# 檢查文件是否存在
if [ ! -f "src/simple_collector.py" ]; then
    echo "❌ 找不到收集器文件"
    exit 1
fi

# 運行收集器
echo "🚀 啟動簡化的 GPU 數據收集器..."
python3 src/simple_collector.py "$@"