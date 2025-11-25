#!/bin/bash
# 簡化的 GPU 視覺化腳本
# 使用重構後的 src/visualization

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 檢查依賴
if ! python3 -c "import matplotlib, pandas, numpy" 2>/dev/null; then
    echo "❌ 缺少必要的依賴，請安裝："
    echo "pip3 install matplotlib pandas numpy"
    exit 1
fi

# 檢查視覺化模塊
if [ ! -f "src/visualization/main.py" ]; then
    echo "❌ 找不到視覺化模塊"
    exit 1
fi

echo "📊 啟動簡化的 GPU 視覺化工具..."
python3 -m src.visualization.main "$@"