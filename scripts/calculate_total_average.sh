#!/bin/bash

# 計算所有節點GPU使用率和VRAM使用率的總平均值
# 支援單日或日期範圍分析

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="$(dirname "$SCRIPT_DIR")/data"

# 節點配置
NODES=("colab-gpu1" "colab-gpu2" "colab-gpu3" "colab-gpu4")

# 顏色輸出
print_info() {
    echo -e "\033[1;34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[1;32m[SUCCESS]\033[0m $1"
}

print_error() {
    echo -e "\033[1;31m[ERROR]\033[0m $1"
}

print_warning() {
    echo -e "\033[1;33m[WARNING]\033[0m $1"
}

show_usage() {
    echo "計算所有節點 GPU 使用率和 VRAM 使用率總平均值"
    echo ""
    echo "使用方法:"
    echo "  $0 [開始日期] [結束日期]"
    echo ""
    echo "參數:"
    echo "  開始日期    分析的起始日期 (YYYY-MM-DD)，預設為今天"
    echo "  結束日期    分析的結束日期 (YYYY-MM-DD)，預設與開始日期相同"
    echo ""
    echo "範例:"
    echo "  $0                           # 分析今天的資料"
    echo "  $0 2025-10-01               # 分析 2025-10-01 的資料"
    echo "  $0 2025-10-01 2025-10-07    # 分析 2025-10-01 到 2025-10-07 期間"
    echo ""
}

# 檢查日期格式
validate_date() {
    local date_str="$1"
    if ! date -d "$date_str" >/dev/null 2>&1; then
        print_error "無效的日期格式: $date_str (需要 YYYY-MM-DD 格式)"
        exit 1
    fi
}

# 計算單日所有節點總平均
calculate_daily_total_average() {
    local date="$1"
    local total_gpu_sum=0
    local total_vram_sum=0
    local total_gpu_count=0
    local total_vram_count=0
    local active_nodes=0
    
    print_info "分析日期: $date"
    echo "========================================"
    
    for node in "${NODES[@]}"; do
        local avg_file="$DATA_DIR/$node/$date/average_$date.csv"
        
        if [[ ! -f "$avg_file" ]]; then
            print_warning "$node: 找不到資料檔案 $avg_file"
            continue
        fi
        
        active_nodes=$((active_nodes + 1))
        
        # 讀取 CSV 檔案，跳過標題行和"全部平均"行
        local node_gpu_sum=0
        local node_vram_sum=0
        local node_gpu_count=0
        local node_vram_count=0
        
        while IFS=',' read -r gpu_id gpu_usage vram_usage user || [[ -n "$gpu_id" ]]; do
            # 跳過標題行和全部平均行
            if [[ "$gpu_id" == "GPU編號" || "$gpu_id" == *"全部平均"* ]]; then
                continue
            fi
            
            # 清理數據（移除可能的空格和引號）
            gpu_usage=$(echo "$gpu_usage" | sed 's/[^0-9.-]//g')
            vram_usage=$(echo "$vram_usage" | sed 's/[^0-9.-]//g')
            
            # 檢查是否為有效數字
            if [[ "$gpu_usage" =~ ^[0-9]+\.?[0-9]*$ ]]; then
                node_gpu_sum=$(awk "BEGIN {print $node_gpu_sum + $gpu_usage}")
                node_gpu_count=$((node_gpu_count + 1))
                total_gpu_sum=$(awk "BEGIN {print $total_gpu_sum + $gpu_usage}")
                total_gpu_count=$((total_gpu_count + 1))
            fi
            
            if [[ "$vram_usage" =~ ^[0-9]+\.?[0-9]*$ ]]; then
                node_vram_sum=$(awk "BEGIN {print $node_vram_sum + $vram_usage}")
                node_vram_count=$((node_vram_count + 1))
                total_vram_sum=$(awk "BEGIN {print $total_vram_sum + $vram_usage}")
                total_vram_count=$((total_vram_count + 1))
            fi
            
        done < "$avg_file"
        
        # 計算該節點平均值
        local node_gpu_avg=0
        local node_vram_avg=0
        
        if [[ $node_gpu_count -gt 0 ]]; then
            node_gpu_avg=$(awk "BEGIN {printf \"%.2f\", $node_gpu_sum / $node_gpu_count}")
        fi
        
        if [[ $node_vram_count -gt 0 ]]; then
            node_vram_avg=$(awk "BEGIN {printf \"%.2f\", $node_vram_sum / $node_vram_count}")
        fi
        
        echo "$node: GPU平均=${node_gpu_avg}% (${node_gpu_count}個GPU), VRAM平均=${node_vram_avg}% (${node_vram_count}個GPU)"
    done
    
    echo "========================================"
    
    # 計算總平均值
    local final_gpu_avg=0
    local final_vram_avg=0
    
    if [[ $total_gpu_count -gt 0 ]]; then
        final_gpu_avg=$(awk "BEGIN {printf \"%.2f\", $total_gpu_sum / $total_gpu_count}")
    fi
    
    if [[ $total_vram_count -gt 0 ]]; then
        final_vram_avg=$(awk "BEGIN {printf \"%.2f\", $total_vram_sum / $total_vram_count}")
    fi
    
    print_success "所有節點總平均 ($date):"
    echo "  🔥 GPU使用率總平均:  ${final_gpu_avg}% (統計${total_gpu_count}個GPU)"
    echo "  💾 VRAM使用率總平均: ${final_vram_avg}% (統計${total_vram_count}個GPU)"
    echo "  📊 活躍節點數量:      ${active_nodes}/${#NODES[@]}"
    echo ""
}

# 計算日期範圍總平均
calculate_range_total_average() {
    local start_date="$1"
    local end_date="$2"
    
    print_info "分析期間: $start_date 至 $end_date"
    echo "========================================"
    
    local range_gpu_sum=0
    local range_vram_sum=0
    local range_gpu_count=0
    local range_vram_count=0
    local total_days=0
    local valid_days=0
    
    # 遍歷日期範圍
    local current_date="$start_date"
    while [[ "$current_date" != $(date -d "$end_date + 1 day" +%Y-%m-%d) ]]; do
        total_days=$((total_days + 1))
        local day_has_data=false
        
        for node in "${NODES[@]}"; do
            local avg_file="$DATA_DIR/$node/$current_date/average_$current_date.csv"
            
            if [[ -f "$avg_file" ]]; then
                day_has_data=true
                
                # 處理該節點的資料
                while IFS=',' read -r gpu_id gpu_usage vram_usage user || [[ -n "$gpu_id" ]]; do
                    # 跳過標題行和全部平均行
                    if [[ "$gpu_id" == "GPU編號" || "$gpu_id" == *"全部平均"* ]]; then
                        continue
                    fi
                    
                    # 清理數據
                    gpu_usage=$(echo "$gpu_usage" | sed 's/[^0-9.-]//g')
                    vram_usage=$(echo "$vram_usage" | sed 's/[^0-9.-]//g')
                    
                    # 累計統計
                    if [[ "$gpu_usage" =~ ^[0-9]+\.?[0-9]*$ ]]; then
                        range_gpu_sum=$(awk "BEGIN {print $range_gpu_sum + $gpu_usage}")
                        range_gpu_count=$((range_gpu_count + 1))
                    fi
                    
                    if [[ "$vram_usage" =~ ^[0-9]+\.?[0-9]*$ ]]; then
                        range_vram_sum=$(awk "BEGIN {print $range_vram_sum + $vram_usage}")
                        range_vram_count=$((range_vram_count + 1))
                    fi
                    
                done < "$avg_file"
            fi
        done
        
        if [[ "$day_has_data" == true ]]; then
            valid_days=$((valid_days + 1))
        fi
        
        current_date=$(date -d "$current_date + 1 day" +%Y-%m-%d)
    done
    
    # 計算範圍總平均
    local range_gpu_avg=0
    local range_vram_avg=0
    
    if [[ $range_gpu_count -gt 0 ]]; then
        range_gpu_avg=$(awk "BEGIN {printf \"%.2f\", $range_gpu_sum / $range_gpu_count}")
    fi
    
    if [[ $range_vram_count -gt 0 ]]; then
        range_vram_avg=$(awk "BEGIN {printf \"%.2f\", $range_vram_sum / $range_vram_count}")
    fi
    
    echo "期間統計: ${valid_days}/${total_days} 天有資料"
    echo "========================================"
    print_success "期間總平均 ($start_date 至 $end_date):"
    echo "  🔥 GPU使用率總平均:  ${range_gpu_avg}% (統計${range_gpu_count}個GPU×天數)"
    echo "  💾 VRAM使用率總平均: ${range_vram_avg}% (統計${range_vram_count}個GPU×天數)"
    echo "  📅 有效數據天數:      ${valid_days} 天"
    echo ""
    
    # 也顯示每日的總平均（簡化版）
    print_info "每日總平均趨勢:"
    echo "日期          GPU平均(%)  VRAM平均(%)"
    echo "--------------------------------------"
    
    current_date="$start_date"
    while [[ "$current_date" != $(date -d "$end_date + 1 day" +%Y-%m-%d) ]]; do
        local daily_gpu_sum=0
        local daily_vram_sum=0
        local daily_gpu_count=0
        local daily_vram_count=0
        
        for node in "${NODES[@]}"; do
            local avg_file="$DATA_DIR/$node/$current_date/average_$current_date.csv"
            
            if [[ -f "$avg_file" ]]; then
                while IFS=',' read -r gpu_id gpu_usage vram_usage user || [[ -n "$gpu_id" ]]; do
                    if [[ "$gpu_id" == "GPU編號" || "$gpu_id" == *"全部平均"* ]]; then
                        continue
                    fi
                    
                    gpu_usage=$(echo "$gpu_usage" | sed 's/[^0-9.-]//g')
                    vram_usage=$(echo "$vram_usage" | sed 's/[^0-9.-]//g')
                    
                    if [[ "$gpu_usage" =~ ^[0-9]+\.?[0-9]*$ ]]; then
                        daily_gpu_sum=$(awk "BEGIN {print $daily_gpu_sum + $gpu_usage}")
                        daily_gpu_count=$((daily_gpu_count + 1))
                    fi
                    
                    if [[ "$vram_usage" =~ ^[0-9]+\.?[0-9]*$ ]]; then
                        daily_vram_sum=$(awk "BEGIN {print $daily_vram_sum + $vram_usage}")
                        daily_vram_count=$((daily_vram_count + 1))
                    fi
                done < "$avg_file"
            fi
        done
        
        local daily_gpu_avg=0
        local daily_vram_avg=0
        
        if [[ $daily_gpu_count -gt 0 ]]; then
            daily_gpu_avg=$(awk "BEGIN {printf \"%.2f\", $daily_gpu_sum / $daily_gpu_count}")
        fi
        
        if [[ $daily_vram_count -gt 0 ]]; then
            daily_vram_avg=$(awk "BEGIN {printf \"%.2f\", $daily_vram_sum / $daily_vram_count}")
        fi
        
        if [[ $daily_gpu_count -gt 0 || $daily_vram_count -gt 0 ]]; then
            printf "%-12s  %8s    %8s\n" "$current_date" "$daily_gpu_avg" "$daily_vram_avg"
        else
            printf "%-12s  %8s    %8s\n" "$current_date" "無資料" "無資料"
        fi
        
        current_date=$(date -d "$current_date + 1 day" +%Y-%m-%d)
    done
    
    echo ""
}

# 主程式
main() {
    local start_date
    local end_date
    
    # 處理命令列參數
    case $# in
        0)
            # 無參數：使用今天
            start_date=$(date +%Y-%m-%d)
            end_date="$start_date"
            ;;
        1)
            # 一個參數：單日分析
            if [[ "$1" == "-h" || "$1" == "--help" ]]; then
                show_usage
                exit 0
            fi
            start_date="$1"
            end_date="$start_date"
            ;;
        2)
            # 兩個參數：日期範圍分析
            start_date="$1"
            end_date="$2"
            ;;
        *)
            print_error "參數錯誤"
            show_usage
            exit 1
            ;;
    esac
    
    # 驗證日期格式
    validate_date "$start_date"
    validate_date "$end_date"
    
    # 確保開始日期不晚於結束日期
    if [[ "$start_date" > "$end_date" ]]; then
        print_error "開始日期 ($start_date) 不能晚於結束日期 ($end_date)"
        exit 1
    fi
    
    # 檢查資料目錄
    if [[ ! -d "$DATA_DIR" ]]; then
        print_error "找不到資料目錄: $DATA_DIR"
        exit 1
    fi
    
    echo "🔥 GPU 和 VRAM 使用率總平均計算工具"
    echo "=========================================="
    
    # 根據日期範圍選擇處理方式
    if [[ "$start_date" == "$end_date" ]]; then
        # 單日分析
        calculate_daily_total_average "$start_date"
    else
        # 日期範圍分析
        calculate_range_total_average "$start_date" "$end_date"
    fi
    
    print_success "分析完成！"
}

# 執行主程式
main "$@"