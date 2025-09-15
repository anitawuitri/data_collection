#!/bin/bash

# GPU 監控系統使用者資訊版本執行腳本
# 版本: v2.0
# 更新日期: 2025-08-06

# 設置腳本選項
set -e

# 顏色配置
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 輔助函數
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo "=================================================="
    echo "  GPU 監控系統 - 使用者資訊版本 v2.0"
    echo "=================================================="
}

# 顯示使用說明
show_usage() {
    echo "使用方法:"
    echo "  $0 <命令> [參數...]"
    echo ""
    echo "命令列表:"
    echo "  collect [日期]           收集 GPU 使用資料（包含使用者資訊）"
    echo "  quick <開始日期> <結束日期>   生成快速視覺化圖表（包含使用者資訊）"
    echo "  plots <開始日期> <結束日期>   生成所有類型圖表（包含使用者資訊）"
    echo "  heatmap <開始日期> <結束日期> 生成 GPU 使用率熱力圖（包含使用者資訊）"
    echo "  vram-users <開始日期> <結束日期> 生成 VRAM 使用者活動摘要"
    echo "  vram-compare <開始日期> <結束日期> 生成 VRAM 節點對比圖（包含使用者資訊）"
    echo "  vram-heatmap <開始日期> <結束日期> 生成 VRAM 熱力圖（包含使用者資訊）"
    echo "  users <開始日期> <結束日期>   僅生成使用者活動摘要圖表"
    echo "  query-user <使用者> <日期>    查詢特定使用者的 GPU 使用情況"
    echo "  query-user <使用者> <開始日期> <結束日期> 查詢使用者多日 GPU 使用情況"
    echo "  list-users <日期>            列出指定日期的所有 GPU 使用者"
    echo "  test                     運行功能測試"
    echo "  test-all                 運行完整測試套件"
    echo "  verify                   驗證圖表檔案"
    echo "  help                     顯示此說明"
    echo ""
    echo "範例:"
    echo "  $0 collect                    # 收集今日資料"
    echo "  $0 collect 2025-08-04         # 收集指定日期資料"
    echo "  $0 quick 2025-08-04 2025-08-05   # 生成快速圖表"
    echo "  $0 plots 2025-08-04 2025-08-05   # 生成所有圖表"
    echo "  $0 heatmap 2025-08-04 2025-08-05 # 生成熱力圖"
    echo "  $0 vram-users 2025-08-04 2025-08-05 # VRAM 使用者摘要"
    echo "  $0 vram-compare 2025-08-04 2025-08-05 # VRAM 節點對比"
    echo "  $0 vram-heatmap 2025-08-04 2025-08-05 # VRAM 熱力圖"
    echo "  $0 users 2025-08-04 2025-08-05   # 使用者活動摘要"
    echo "  $0 query-user paslab_openai 2025-08-15 # 查詢特定使用者"
    echo "  $0 query-user itrd 2025-07-20 2025-07-25 # 查詢使用者多日"
    echo "  $0 list-users 2025-08-15     # 列出所有使用者"
    echo "  $0 test                       # 運行測試"
    echo "  $0 test-all                   # 運行完整測試套件"
}

# 檢查 Python 環境
check_python_env() {
    print_info "檢查 Python 環境..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安裝"
        exit 1
    fi
    
    # 檢查必要的 Python 套件
    python3 -c "import pandas, matplotlib, seaborn, requests" 2>/dev/null || {
        print_error "缺少必要的 Python 套件，請安裝 requirements.txt"
        exit 1
    }
    
    print_success "Python 環境檢查通過"
}

# 收集資料
collect_data() {
    local date=$1
    print_info "收集 GPU 使用資料..."
    
    cd python
    if [ -z "$date" ]; then
        python3 daily_gpu_log.py
    else
        python3 daily_gpu_log.py "$date"
    fi
    cd ..
    
    print_success "資料收集完成"
}

# 生成快速圖表
generate_quick_plots() {
    local start_date=$1
    local end_date=$2
    
    print_info "生成快速視覺化圖表（包含使用者資訊）..."
    
    cd visualization
    python3 quick_gpu_trend_plots.py "$start_date" "$end_date"
    cd ..
    
    print_success "快速圖表生成完成"
}

# 生成所有圖表
generate_all_plots() {
    local start_date=$1
    local end_date=$2
    
    print_info "生成所有類型圖表（包含使用者資訊）..."
    
    cd visualization
    python3 -c "
from quick_gpu_trend_plots import *

# 生成所有類型的圖表
print('1. 生成節點對比圖表...')
quick_nodes_trend('$start_date', '$end_date', show_users=True)

print('2. 生成各節點 GPU 詳情圖表...')
nodes = ['colab-gpu1', 'colab-gpu2', 'colab-gpu3', 'colab-gpu4']
for node in nodes:
    quick_single_node_gpus(node, '$start_date', '$end_date', show_users=True)

print('3. 生成跨節點 GPU 比較圖表...')
for gpu_idx in range(8):
    quick_gpu_across_nodes(gpu_idx, '$start_date', '$end_date', show_users=True)

print('4. 生成使用者活動摘要圖表...')
quick_user_activity_summary('$start_date', '$end_date')

print('所有圖表生成完成！')
"
    cd ..
    
    print_success "所有圖表生成完成"
}

# 生成熱力圖
generate_heatmap() {
    local start_date=$1
    local end_date=$2
    
    print_info "生成 GPU 使用率熱力圖（包含使用者資訊）..."
    
    cd visualization
    python3 -c "
from quick_gpu_trend_plots import quick_gpu_heatmap
quick_gpu_heatmap('$start_date', '$end_date', show_users=True)
print('GPU 使用率熱力圖生成完成！')
"
    cd ..
    
    print_success "熱力圖生成完成"
}

# 生成 VRAM 使用者活動摘要
generate_vram_user_summary() {
    local start_date=$1
    local end_date=$2
    
    print_info "生成 VRAM 使用者活動摘要圖表..."
    
    cd visualization
    python3 -c "
from quick_gpu_trend_plots import quick_vram_user_activity_summary
path = quick_vram_user_activity_summary('$start_date', '$end_date')
if path:
    print('VRAM 使用者活動摘要圖表生成完成！')
    print(f'保存至: {path}')
else:
    print('VRAM 使用者活動摘要圖表生成失敗')
"
    cd ..
    
    print_success "VRAM 使用者活動摘要生成完成"
}

# 生成 VRAM 節點對比圖
generate_vram_comparison() {
    local start_date=$1
    local end_date=$2
    
    print_info "生成 VRAM 節點對比圖（包含使用者資訊）..."
    
    cd visualization
    python3 -c "
from quick_gpu_trend_plots import quick_vram_nodes_comparison_with_users
path = quick_vram_nodes_comparison_with_users('$start_date', '$end_date', show_users=True)
if path:
    print('VRAM 節點對比圖表生成完成！')
    print(f'保存至: {path}')
else:
    print('VRAM 節點對比圖表生成失敗')
"
    cd ..
    
    print_success "VRAM 節點對比圖生成完成"
}

# 生成 VRAM 熱力圖
generate_vram_heatmap() {
    local start_date=$1
    local end_date=$2
    
    print_info "生成 VRAM 熱力圖（包含使用者資訊）..."
    
    cd visualization
    python3 -c "
from quick_gpu_trend_plots import quick_vram_heatmap
path = quick_vram_heatmap('$start_date', '$end_date', show_users=True)
if path:
    print('VRAM 熱力圖生成完成！')
    print(f'保存至: {path}')
else:
    print('VRAM 熱力圖生成失敗')
"
    cd ..
    
    print_success "VRAM 熱力圖生成完成"
}

# 生成使用者活動摘要
generate_user_summary() {
    local start_date=$1
    local end_date=$2
    
    print_info "生成使用者活動摘要圖表..."
    
    cd visualization
    python3 -c "
from quick_gpu_trend_plots import quick_user_activity_summary
quick_user_activity_summary('$start_date', '$end_date')
print('使用者活動摘要圖表生成完成！')
"
    cd ..
    
    print_success "使用者活動摘要生成完成"
}

# 運行測試
run_tests() {
    print_info "運行功能測試..."
    
    cd visualization
    python3 test_user_info.py
    cd ..
    
    print_success "功能測試完成"
}

# 運行完整測試套件
run_all_tests() {
    print_info "運行完整測試套件..."
    
    cd test_cases
    python3 run_all_tests.py
    cd ..
    
    print_success "完整測試套件執行完成"
}

# 驗證圖表
verify_charts() {
    print_info "驗證圖表檔案..."
    
    cd test_cases
    python3 chart_verification.py
    cd ..
    
    print_success "圖表驗證完成"
}

# 檢查日期格式
validate_date() {
    local date=$1
    if [[ ! $date =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
        print_error "日期格式錯誤，請使用 YYYY-MM-DD 格式"
        exit 1
    fi
}

# 主程式
main() {
    print_header
    
    if [ $# -eq 0 ]; then
        show_usage
        exit 1
    fi
    
    local command=$1
    shift
    
    case $command in
        "collect")
            check_python_env
            local date=$1
            if [ -n "$date" ]; then
                validate_date "$date"
            fi
            collect_data "$date"
            ;;
        "quick")
            if [ $# -ne 2 ]; then
                print_error "quick 命令需要開始日期和結束日期"
                show_usage
                exit 1
            fi
            check_python_env
            validate_date "$1"
            validate_date "$2"
            generate_quick_plots "$1" "$2"
            ;;
        "plots")
            if [ $# -ne 2 ]; then
                print_error "plots 命令需要開始日期和結束日期"
                show_usage
                exit 1
            fi
            check_python_env
            validate_date "$1"
            validate_date "$2"
            generate_all_plots "$1" "$2"
            ;;
        "heatmap")
            if [ $# -ne 2 ]; then
                print_error "heatmap 命令需要開始日期和結束日期"
                show_usage
                exit 1
            fi
            check_python_env
            validate_date "$1"
            validate_date "$2"
            generate_heatmap "$1" "$2"
            ;;
        "vram-users")
            if [ $# -ne 2 ]; then
                print_error "vram-users 命令需要開始日期和結束日期"
                show_usage
                exit 1
            fi
            check_python_env
            validate_date "$1"
            validate_date "$2"
            generate_vram_user_summary "$1" "$2"
            ;;
        "vram-compare")
            if [ $# -ne 2 ]; then
                print_error "vram-compare 命令需要開始日期和結束日期"
                show_usage
                exit 1
            fi
            check_python_env
            validate_date "$1"
            validate_date "$2"
            generate_vram_comparison "$1" "$2"
            ;;
        "vram-heatmap")
            if [ $# -ne 2 ]; then
                print_error "vram-heatmap 命令需要開始日期和結束日期"
                show_usage
                exit 1
            fi
            check_python_env
            validate_date "$1"
            validate_date "$2"
            generate_vram_heatmap "$1" "$2"
            ;;
        "users")
            if [ $# -ne 2 ]; then
                print_error "users 命令需要開始日期和結束日期"
                show_usage
                exit 1
            fi
            check_python_env
            validate_date "$1"
            validate_date "$2"
            generate_user_summary "$1" "$2"
            ;;
        "query-user")
            if [ $# -lt 2 ] || [ $# -gt 3 ]; then
                print_error "query-user 命令格式: query-user <使用者> <日期> 或 query-user <使用者> <開始日期> <結束日期>"
                show_usage
                exit 1
            fi
            check_python_env
            local username=$1
            local start_date=$2
            local end_date=$3
            validate_date "$start_date"
            if [ -n "$end_date" ]; then
                validate_date "$end_date"
                python3 get_user_gpu_usage.py "$username" "$start_date" "$end_date"
            else
                python3 get_user_gpu_usage.py "$username" "$start_date"
            fi
            ;;
        "list-users")
            if [ $# -ne 1 ]; then
                print_error "list-users 命令需要一個日期參數"
                show_usage
                exit 1
            fi
            check_python_env
            validate_date "$1"
            python3 get_user_gpu_usage.py --list-users "$1"
            ;;
        "test")
            check_python_env
            run_tests
            ;;
        "test-all")
            check_python_env
            run_all_tests
            ;;
        "verify")
            check_python_env
            verify_charts
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            print_error "未知命令: $command"
            show_usage
            exit 1
            ;;
    esac
}

# 執行主程式
main "$@"
