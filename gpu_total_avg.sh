#!/bin/bash

# 快速計算所有節點總平均的便捷腳本
# 自動選擇最近的資料日期

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOTAL_AVG_SCRIPT="$SCRIPT_DIR/scripts/calculate_total_average.sh"
DATA_DIR="$SCRIPT_DIR/data"

print_info() {
    echo -e "\033[1;34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[1;32m[SUCCESS]\033[0m $1"
}

print_error() {
    echo -e "\033[1;31m[ERROR]\033[0m $1"
}

# 找到最近的資料日期
find_latest_data_date() {
    local latest_date=""
    
    # 檢查各節點的資料目錄，找到最新的日期
    for node in colab-gpu1 colab-gpu2 colab-gpu3 colab-gpu4; do
        local node_dir="$DATA_DIR/$node"
        if [[ -d "$node_dir" ]]; then
            for date_dir in $(ls "$node_dir" 2>/dev/null | grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' | sort -r); do
                if [[ -f "$node_dir/$date_dir/average_$date_dir.csv" ]]; then
                    if [[ -z "$latest_date" ]] || [[ "$date_dir" > "$latest_date" ]]; then
                        latest_date="$date_dir"
                    fi
                fi
            done
        fi
    done
    
    echo "$latest_date"
}

# 顯示使用說明
show_usage() {
    echo "🔥 GPU 和 VRAM 總平均快速查詢工具"
    echo "====================================="
    echo ""
    echo "使用方法:"
    echo "  $0 [模式] [參數...]"
    echo ""
    echo "模式:"
    echo "  latest, l        查看最近一天的總平均（預設）"
    echo "  recent, r        查看最近7天的總平均"
    echo "  week, w          查看最近一週的總平均"
    echo "  custom [日期]    查看指定日期或日期範圍的總平均"
    echo "  help, -h         顯示此說明"
    echo ""
    echo "範例:"
    echo "  $0                           # 最近一天的總平均"
    echo "  $0 latest                    # 最近一天的總平均"
    echo "  $0 recent                    # 最近7天的總平均"
    echo "  $0 custom 2025-10-24         # 指定日期"
    echo "  $0 custom 2025-10-20 2025-10-24  # 指定範圍"
    echo ""
}

# 主程式
main() {
    local mode="${1:-latest}"
    
    case "$mode" in
        "latest"|"l")
            local latest_date=$(find_latest_data_date)
            if [[ -z "$latest_date" ]]; then
                print_error "找不到任何 GPU 使用率資料"
                exit 1
            fi
            
            print_info "查看最近一天的資料: $latest_date"
            echo ""
            "$TOTAL_AVG_SCRIPT" "$latest_date"
            ;;
            
        "recent"|"r"|"week"|"w")
            local latest_date=$(find_latest_data_date)
            if [[ -z "$latest_date" ]]; then
                print_error "找不到任何 GPU 使用率資料"
                exit 1
            fi
            
            # 計算7天前的日期
            local start_date=$(date -d "$latest_date - 6 days" +%Y-%m-%d)
            
            print_info "查看最近7天的資料: $start_date 至 $latest_date"
            echo ""
            "$TOTAL_AVG_SCRIPT" "$start_date" "$latest_date"
            ;;
            
        "custom"|"c")
            shift
            if [[ $# -eq 0 ]]; then
                print_error "custom 模式需要指定日期參數"
                show_usage
                exit 1
            fi
            
            print_info "查看自訂日期的資料"
            echo ""
            "$TOTAL_AVG_SCRIPT" "$@"
            ;;
            
        "help"|"-h"|"--help")
            show_usage
            ;;
            
        *)
            # 如果第一個參數看起來像日期，則直接傳給總平均腳本
            if [[ "$1" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
                print_info "查看指定日期的資料"
                echo ""
                "$TOTAL_AVG_SCRIPT" "$@"
            else
                print_error "未知的模式: $mode"
                show_usage
                exit 1
            fi
            ;;
    esac
}

# 執行主程式
main "$@"