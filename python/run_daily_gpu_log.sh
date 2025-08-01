#!/bin/bash
# Python 版本的 GPU 數據收集執行腳本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PYTHON_SCRIPT="$SCRIPT_DIR/daily_gpu_log.py"

# 顏色輸出函數
print_info() {
    echo -e "\033[1;34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[1;32m[SUCCESS]\033[0m $1"
}

print_error() {
    echo -e "\033[1;31m[ERROR]\033[0m $1"
}

echo "=== AMD GPU 數據收集工具 (Python 版本) ==="
echo ""

# 檢查 Python 環境
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "未找到 python3，請安裝 Python 3.7+"
        exit 1
    fi
    
    # 檢查必要套件
    python3 -c "import requests, pandas" 2>/dev/null || {
        print_error "缺少必要的 Python 套件"
        print_info "請執行以下命令安裝依賴：pip3 install -r $SCRIPT_DIR/requirements.txt"
        exit 1
    }
}

# 顯示使用說明
show_usage() {
    echo "使用方法:"
    echo "  $0 [日期]"
    echo ""
    echo "參數:"
    echo "  日期    可選，格式為 YYYY-MM-DD (例如: 2025-08-01)"
    echo "          如不指定，則使用今天日期"
    echo ""
    echo "範例:"
    echo "  $0                  # 收集今天的數據"
    echo "  $0 2025-08-01      # 收集指定日期的數據"
    echo "  $0 --help          # 顯示此說明"
    echo ""
}

# 主程式
main() {
    if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
        show_usage
        exit 0
    fi
    
    # 檢查環境
    check_python
    
    # 切換到專案根目錄（確保相對路徑正確）
    cd "$PROJECT_ROOT"
    
    # 執行 Python 腳本
    print_info "啟動 Python 數據收集器..."
    python3 "$PYTHON_SCRIPT" "$@"
    
    if [ $? -eq 0 ]; then
        print_success "數據收集完成！"
    else
        print_error "數據收集失敗"
        exit 1
    fi
}

# 執行主程式
main "$@"
