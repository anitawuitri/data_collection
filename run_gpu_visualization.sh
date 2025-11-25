#!/bin/bash

# ================================
# GPU視覺化工具包裝器
# ================================
# 重構版 - 使用 Python 高級視覺化工具
# 這個腳本現在是一個簡單包裝器，調用 src/tools/advanced_visualizer.py
# ================================

set -e

# 腳本目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 顏色設定
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 工具函數
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# 檢查 Python 工具是否存在
check_python_tool() {
    if [[ ! -f "src/tools/advanced_visualizer.py" ]]; then
        log_error "找不到 Python 視覺化工具: src/tools/advanced_visualizer.py"
        return 1
    fi
    
    if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"; then
        log_error "需要 Python 3.8 或更高版本"
        return 1
    fi
    
    return 0
}

# 顯示使用說明
show_usage() {
    cat << 'EOF'
GPU使用狀況視覺化腳本 (重構版)

用法: ./run_gpu_visualization.sh [模式] [選項]

模式:
    quick START_DATE END_DATE    快速生成常用圖表
    nodes START_DATE END_DATE    節點比較視圖
    node NODE_NAME START_DATE END_DATE  單節點分析
    auto                         自動模式(檢測數據並生成圖表)
    test                         環境測試

選項:
    --data-dir DIR              資料目錄 (預設: ./data)
    --output-dir DIR            輸出目錄 (預設: ./plots)
    --nodes NODES               指定節點,逗號分隔 (僅用於quick模式)

範例:
    # 自動模式
    ./run_gpu_visualization.sh auto
    
    # 快速生成圖表
    ./run_gpu_visualization.sh quick 2025-09-15 2025-09-19
    
    # 節點比較
    ./run_gpu_visualization.sh nodes 2025-09-15 2025-09-19
    
    # 單節點分析
    ./run_gpu_visualization.sh node colab-gpu1 2025-09-15 2025-09-19
    
    # 環境測試
    ./run_gpu_visualization.sh test

傳統兼容模式 (將被移除):
    ./run_gpu_visualization.sh [舊選項] [舊模式]
    
    這些舊選項會自動轉換到新格式:
    -s --start-date, -e --end-date, -v --verbose, etc.
EOF
}

# 檢查舊格式參數並轉換
convert_legacy_args() {
    local args=()
    local mode=""
    local start_date=""
    local end_date=""
    local data_dir="./data"
    local output_dir="./plots"
    local nodes=""
    local show_legacy_warning=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            # 舊格式選項
            -s|--start-date)
                start_date="$2"
                show_legacy_warning=true
                shift 2
                ;;
            -e|--end-date)
                end_date="$2"
                show_legacy_warning=true
                shift 2
                ;;
            -n|--nodes)
                nodes="$2"
                show_legacy_warning=true
                shift 2
                ;;
            -d|--data-dir)
                data_dir="$2"
                shift 2
                ;;
            -o|--output-dir)
                output_dir="$2"
                shift 2
                ;;
            -u|--show-users)
                log_warn "show-users 選項已整合到視覺化工具中"
                show_legacy_warning=true
                shift
                ;;
            -v|--verbose)
                log_warn "verbose 選項已整合到視覺化工具中"  
                show_legacy_warning=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            # 舊格式模式
            quick|nodes|vram-stacked|test-fonts|test-env|auto)
                mode="$1"
                show_legacy_warning=true
                shift
                ;;
            # 新格式直接傳遞
            *)
                args+=("$1")
                shift
                ;;
        esac
    done
    
    # 顯示警告
    if [[ "$show_legacy_warning" == "true" ]]; then
        log_warn "偵測到舊格式參數，正在轉換..."
        log_warn "建議使用新格式: ./run_gpu_visualization.sh [mode] [args]"
    fi
    
    # 轉換舊模式到新格式
    if [[ -n "$mode" ]]; then
        case "$mode" in
            "auto")
                args=("auto" "--data-dir" "$data_dir" "--output-dir" "$output_dir")
                ;;
            "quick")
                if [[ -n "$start_date" && -n "$end_date" ]]; then
                    args=("quick" "$start_date" "$end_date" "--data-dir" "$data_dir" "--output-dir" "$output_dir")
                    if [[ -n "$nodes" ]]; then
                        args+=("--nodes" "$nodes")
                    fi
                else
                    log_error "quick 模式需要指定開始和結束日期"
                    exit 1
                fi
                ;;
            "nodes")
                if [[ -n "$start_date" && -n "$end_date" ]]; then
                    args=("nodes" "$start_date" "$end_date" "--data-dir" "$data_dir" "--output-dir" "$output_dir")
                else
                    log_error "nodes 模式需要指定開始和結束日期"
                    exit 1
                fi
                ;;
            "vram-stacked")
                log_warn "vram-stacked 模式已整合到 quick 模式中"
                if [[ -n "$start_date" && -n "$end_date" ]]; then
                    args=("quick" "$start_date" "$end_date" "--data-dir" "$data_dir" "--output-dir" "$output_dir")
                else
                    args=("auto" "--data-dir" "$data_dir" "--output-dir" "$output_dir")
                fi
                ;;
            "test-fonts"|"test-env")
                args=("test" "--data-dir" "$data_dir" "--output-dir" "$output_dir")
                ;;
        esac
    fi
    
    # 如果沒有參數，預設為 auto
    if [[ ${#args[@]} -eq 0 ]]; then
        args=("auto")
    fi
    
    # 設定全域變數供 main 函數使用
    CONVERTED_ARGS=("${args[@]}")
}

# 主函數
main() {
    log_info "GPU視覺化工具 (重構版)"
    
    # 檢查 Python 工具
    if ! check_python_tool; then
        exit 1
    fi
    
    # 轉換舊格式參數
    convert_legacy_args "$@"
    
    # 顯示即將執行的命令
    log_info "執行: python3 -m src.tools.advanced_visualizer ${CONVERTED_ARGS[*]}"
    
    # 執行 Python 工具
    if python3 -m src.tools.advanced_visualizer "${CONVERTED_ARGS[@]}"; then
        log_info "視覺化完成!"
    else
        log_error "視覺化失敗"
        exit 1
    fi
}

# 如果直接執行此腳本
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi