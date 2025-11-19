#!/bin/bash

# colab-gpu 1-4 節點 GPU 使用率和 VRAM 使用率總平均計算工具
# 專門針對 colab-gpu1, colab-gpu2, colab-gpu3, colab-gpu4 節點的統計分析

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="$SCRIPT_DIR/data"

# colab-gpu 節點配置
COLAB_NODES=("colab-gpu1" "colab-gpu2" "colab-gpu3" "colab-gpu4")
NODE_IPS=("192.168.10.103" "192.168.10.104" "192.168.10.105" "192.168.10.106")

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
    echo "🔥 colab-gpu 1-4 節點 GPU 和 VRAM 使用率總平均計算工具"
    echo "============================================================"
    echo ""
    echo "使用方法:"
    echo "  $0 [模式] [開始日期] [結束日期]"
    echo ""
    echo "模式:"
    echo "  summary, s       顯示簡潔的總平均摘要（預設）"
    echo "  detailed, d      顯示詳細的節點分析"
    echo "  individual, i    顯示各節點各自的總平均"
    echo "  user, u          顯示各使用者的平均使用率（新功能）"
    echo "  trend, t         顯示趨勢分析（適用於日期範圍）"
    echo "  export, e        匯出CSV格式數據"
    echo "  help, -h         顯示此說明"
    echo ""
    echo "參數:"
    echo "  開始日期    分析的起始日期 (YYYY-MM-DD)，預設為最新資料日期"
    echo "  結束日期    分析的結束日期 (YYYY-MM-DD)，預設與開始日期相同"
    echo ""
    echo "範例:"
    echo "  $0                           # 最新資料的簡潔總平均"
    echo "  $0 detailed                  # 最新資料的詳細分析"
    echo "  $0 individual                # 最新資料的各節點總平均"
    echo "  $0 summary 2025-10-24       # 指定日期的總平均"
    echo "  $0 individual 2025-10-20 2025-10-24  # 各節點日期範圍總平均"
    echo "  $0 trend 2025-10-20 2025-10-24  # 日期範圍的趨勢分析"
    echo "  $0 export 2025-10-20 2025-10-24 # 匯出CSV數據"
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

# 找到最新的資料日期
find_latest_data_date() {
    local latest_date=""
    
    for node in "${COLAB_NODES[@]}"; do
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

# 計算單日節點統計
calculate_daily_node_stats() {
    local date="$1"
    local total_gpu_sum=0
    local total_vram_sum=0
    local total_gpu_count=0
    local total_vram_count=0
    local active_nodes=0
    
    declare -A node_stats
    
    for i in "${!COLAB_NODES[@]}"; do
        local node="${COLAB_NODES[$i]}"
        local node_ip="${NODE_IPS[$i]}"
        local avg_file="$DATA_DIR/$node/$date/average_$date.csv"
        
        if [[ ! -f "$avg_file" ]]; then
            node_stats["${node}_status"]="無資料"
            continue
        fi
        
        active_nodes=$((active_nodes + 1))
        node_stats["${node}_status"]="正常"
        
        local node_gpu_sum=0
        local node_vram_sum=0
        local node_gpu_count=0
        local node_vram_count=0
        local active_gpus=0
        
        while IFS=',' read -r gpu_id gpu_usage vram_usage user || [[ -n "$gpu_id" ]]; do
            if [[ "$gpu_id" == "GPU編號" || "$gpu_id" == *"全部平均"* ]]; then
                continue
            fi
            
            gpu_usage=$(echo "$gpu_usage" | sed 's/[^0-9.-]//g')
            vram_usage=$(echo "$vram_usage" | sed 's/[^0-9.-]//g')
            
            if [[ "$gpu_usage" =~ ^[0-9]+\.?[0-9]*$ ]]; then
                node_gpu_sum=$(awk "BEGIN {print $node_gpu_sum + $gpu_usage}")
                node_gpu_count=$((node_gpu_count + 1))
                total_gpu_sum=$(awk "BEGIN {print $total_gpu_sum + $gpu_usage}")
                total_gpu_count=$((total_gpu_count + 1))
                
                # 統計活躍GPU（使用率>1%）
                if (( $(awk "BEGIN {print ($gpu_usage > 1)}") )); then
                    active_gpus=$((active_gpus + 1))
                fi
            fi
            
            if [[ "$vram_usage" =~ ^[0-9]+\.?[0-9]*$ ]]; then
                node_vram_sum=$(awk "BEGIN {print $node_vram_sum + $vram_usage}")
                node_vram_count=$((node_vram_count + 1))
                total_vram_sum=$(awk "BEGIN {print $total_vram_sum + $vram_usage}")
                total_vram_count=$((total_vram_count + 1))
            fi
            
        done < "$avg_file"
        
        # 計算節點平均值
        if [[ $node_gpu_count -gt 0 ]]; then
            node_stats["${node}_gpu_avg"]=$(awk "BEGIN {printf \"%.2f\", $node_gpu_sum / $node_gpu_count}")
            node_stats["${node}_gpu_count"]=$node_gpu_count
            node_stats["${node}_active_gpus"]=$active_gpus
        else
            node_stats["${node}_gpu_avg"]="0.00"
            node_stats["${node}_gpu_count"]=0
            node_stats["${node}_active_gpus"]=0
        fi
        
        if [[ $node_vram_count -gt 0 ]]; then
            node_stats["${node}_vram_avg"]=$(awk "BEGIN {printf \"%.2f\", $node_vram_sum / $node_vram_count}")
            node_stats["${node}_vram_count"]=$node_vram_count
        else
            node_stats["${node}_vram_avg"]="0.00"
            node_stats["${node}_vram_count"]=0
        fi
        
        node_stats["${node}_ip"]=$node_ip
    done
    
    # 計算總平均值
    local final_gpu_avg=0
    local final_vram_avg=0
    
    if [[ $total_gpu_count -gt 0 ]]; then
        final_gpu_avg=$(awk "BEGIN {printf \"%.2f\", $total_gpu_sum / $total_gpu_count}")
    fi
    
    if [[ $total_vram_count -gt 0 ]]; then
        final_vram_avg=$(awk "BEGIN {printf \"%.2f\", $total_vram_sum / $total_vram_count}")
    fi
    
    # 輸出結果到全域變數
    DAILY_GPU_AVG=$final_gpu_avg
    DAILY_VRAM_AVG=$final_vram_avg
    DAILY_GPU_COUNT=$total_gpu_count
    DAILY_VRAM_COUNT=$total_vram_count
    DAILY_ACTIVE_NODES=$active_nodes
    
    # 複製節點統計到全域
    for key in "${!node_stats[@]}"; do
        DAILY_NODE_STATS[$key]=${node_stats[$key]}
    done
}

# 簡潔摘要模式
show_summary() {
    local date="$1"
    
    declare -A DAILY_NODE_STATS
    calculate_daily_node_stats "$date"
    
    echo "🔥 colab-gpu 1-4 節點總平均摘要"
    echo "================================="
    echo "📅 分析日期: $date"
    echo ""
    echo "📊 總平均結果:"
    echo "  🔥 GPU使用率:  ${DAILY_GPU_AVG}% (${DAILY_GPU_COUNT}個GPU)"
    echo "  💾 VRAM使用率: ${DAILY_VRAM_AVG}% (${DAILY_VRAM_COUNT}個GPU)"
    echo "  🖥️  活躍節點:   ${DAILY_ACTIVE_NODES}/4"
    echo ""
    
    # 計算總活躍GPU數
    local total_active_gpus=0
    for node in "${COLAB_NODES[@]}"; do
        local active_key="${node}_active_gpus"
        if [[ -n "${DAILY_NODE_STATS[$active_key]}" ]]; then
            total_active_gpus=$((total_active_gpus + ${DAILY_NODE_STATS[$active_key]}))
        fi
    done
    
    echo "📈 快速統計:"
    echo "  ⚡ 活躍GPU:    ${total_active_gpus}/${DAILY_GPU_COUNT} (使用率>1%)"
    echo "  💤 閒置GPU:    $((DAILY_GPU_COUNT - total_active_gpus))/${DAILY_GPU_COUNT}"
    echo "  🔋 資源利用率: $(awk "BEGIN {printf \"%.1f\", ($total_active_gpus / $DAILY_GPU_COUNT) * 100}")%"
    echo ""
}

# 詳細分析模式
show_detailed() {
    local date="$1"
    
    declare -A DAILY_NODE_STATS
    calculate_daily_node_stats "$date"
    
    echo "🔥 colab-gpu 1-4 節點詳細分析"
    echo "==============================="
    echo "📅 分析日期: $date"
    echo ""
    
    echo "📊 各節點詳細統計:"
    echo "節點          IP地址          GPU使用率  VRAM使用率  活躍GPU  狀態"
    echo "-----------------------------------------------------------------------"
    
    for node in "${COLAB_NODES[@]}"; do
        local status="${DAILY_NODE_STATS[${node}_status]:-未知}"
        local ip="${DAILY_NODE_STATS[${node}_ip]:-N/A}"
        local gpu_avg="${DAILY_NODE_STATS[${node}_gpu_avg]:-0.00}"
        local vram_avg="${DAILY_NODE_STATS[${node}_vram_avg]:-0.00}"
        local active_gpus="${DAILY_NODE_STATS[${node}_active_gpus]:-0}"
        local gpu_count="${DAILY_NODE_STATS[${node}_gpu_count]:-8}"
        
        printf "%-12s  %-15s  %8s%%    %8s%%    %2s/%-2s    %s\n" \
               "$node" "$ip" "$gpu_avg" "$vram_avg" "$active_gpus" "$gpu_count" "$status"
    done
    
    echo ""
    echo "🎯 總平均結果:"
    echo "  🔥 GPU使用率總平均:  ${DAILY_GPU_AVG}% (統計${DAILY_GPU_COUNT}個GPU)"
    echo "  💾 VRAM使用率總平均: ${DAILY_VRAM_AVG}% (統計${DAILY_VRAM_COUNT}個GPU)"
    echo "  🖥️  正常運作節點:     ${DAILY_ACTIVE_NODES}/4"
    echo ""
}

# 各節點個別總平均分析模式
show_individual() {
    local start_date="$1"
    local end_date="$2"
    
    # 如果沒有結束日期，設定為開始日期
    if [[ -z "$end_date" ]]; then
        end_date="$start_date"
    fi
    
    echo "🔥 colab-gpu 1-4 各節點個別總平均"
    echo "=================================="
    
    if [[ "$start_date" == "$end_date" ]]; then
        echo "📅 分析日期: $start_date"
    else
        echo "📅 分析期間: $start_date 至 $end_date"
    fi
    echo ""
    
    echo "📊 各節點個別總平均統計:"
    echo "節點          GPU總平均(%)  VRAM總平均(%)  分析天數  資料完整度"
    echo "----------------------------------------------------------------"
    
    # 為每個節點計算個別總平均
    for node in "${COLAB_NODES[@]}"; do
        local node_dir="$DATA_DIR/$node"
        local gpu_sum=0
        local vram_sum=0
        local gpu_count=0
        local vram_count=0
        local valid_days=0
        local total_days=0
        
        # 遍歷日期範圍
        local current_date="$start_date"
        while [[ "$current_date" < "$end_date" ]] || [[ "$current_date" == "$end_date" ]]; do
            total_days=$((total_days + 1))
            local date_dir="$node_dir/$current_date"
            local avg_file="$date_dir/average_$current_date.csv"
            
            if [[ -f "$avg_file" ]]; then
                valid_days=$((valid_days + 1))
                
                # 讀取平均值文件並計算總和
                while IFS=',' read -r gpu_idx gpu_util vram_util user || [[ -n "$gpu_idx" ]]; do
                    if [[ "$gpu_idx" =~ ^GPU\[[0-9]+\]$ ]] && [[ "$gpu_util" =~ ^[0-9]+\.?[0-9]*$ ]] && [[ "$vram_util" =~ ^[0-9]+\.?[0-9]*$ ]]; then
                        gpu_sum=$(awk "BEGIN {printf \"%.6f\", $gpu_sum + $gpu_util}")
                        vram_sum=$(awk "BEGIN {printf \"%.6f\", $vram_sum + $vram_util}")
                        gpu_count=$((gpu_count + 1))
                        vram_count=$((vram_count + 1))
                    fi
                done < "$avg_file"
            fi
            
            # 移動到下一天
            current_date=$(date -d "$current_date + 1 day" "+%Y-%m-%d")
        done
        
        # 計算平均值
        local node_gpu_avg="0.00"
        local node_vram_avg="0.00"
        local data_completeness="0"
        
        if [[ $gpu_count -gt 0 ]]; then
            node_gpu_avg=$(awk "BEGIN {printf \"%.2f\", $gpu_sum / $gpu_count}")
        fi
        
        if [[ $vram_count -gt 0 ]]; then
            node_vram_avg=$(awk "BEGIN {printf \"%.2f\", $vram_sum / $vram_count}")
        fi
        
        if [[ $total_days -gt 0 ]]; then
            data_completeness=$(awk "BEGIN {printf \"%.0f\", ($valid_days / $total_days) * 100}")
        fi
        
        # 格式化輸出
        printf "%-12s  %10s%%    %11s%%      %4d      %6s%%\n" \
               "$node" \
               "$node_gpu_avg" \
               "$node_vram_avg" \
               "$valid_days" \
               "$data_completeness"
    done
    
    echo ""
    echo "📈 總結:"
    
    # 計算所有節點的總體統計
    local total_gpu_sum=0
    local total_vram_sum=0
    local total_gpu_count=0
    local total_vram_count=0
    local total_valid_days=0
    local total_possible_days=0
    
    for node in "${COLAB_NODES[@]}"; do
        local node_dir="$DATA_DIR/$node"
        local current_date="$start_date"
        
        while [[ "$current_date" < "$end_date" ]] || [[ "$current_date" == "$end_date" ]]; do
            total_possible_days=$((total_possible_days + 1))
            local avg_file="$node_dir/$current_date/average_$current_date.csv"
            
            if [[ -f "$avg_file" ]]; then
                total_valid_days=$((total_valid_days + 1))
                
                while IFS=',' read -r gpu_idx gpu_util vram_util user || [[ -n "$gpu_idx" ]]; do
                    if [[ "$gpu_idx" =~ ^GPU\[[0-9]+\]$ ]] && [[ "$gpu_util" =~ ^[0-9]+\.?[0-9]*$ ]] && [[ "$vram_util" =~ ^[0-9]+\.?[0-9]*$ ]]; then
                        total_gpu_sum=$(awk "BEGIN {printf \"%.6f\", $total_gpu_sum + $gpu_util}")
                        total_vram_sum=$(awk "BEGIN {printf \"%.6f\", $total_vram_sum + $vram_util}")
                        total_gpu_count=$((total_gpu_count + 1))
                        total_vram_count=$((total_vram_count + 1))
                    fi
                done < "$avg_file"
            fi
            
            current_date=$(date -d "$current_date + 1 day" "+%Y-%m-%d")
        done
    done
    
    # 顯示整體總平均
    if [[ $total_gpu_count -gt 0 ]] && [[ $total_vram_count -gt 0 ]]; then
        local overall_gpu_avg=$(awk "BEGIN {printf \"%.2f\", $total_gpu_sum / $total_gpu_count}")
        local overall_vram_avg=$(awk "BEGIN {printf \"%.2f\", $total_vram_sum / $total_vram_count}")
        local overall_completeness=$(awk "BEGIN {printf \"%.1f\", ($total_valid_days / $total_possible_days) * 100}")
        
        echo "  🎯 四節點整體總平均: GPU ${overall_gpu_avg}%, VRAM ${overall_vram_avg}%"
        echo "  📊 資料完整度: ${overall_completeness}% (${total_valid_days}/${total_possible_days} 節點×天數)"
    else
        echo "  ⚠️  無法計算整體總平均：缺少有效數據"
    fi
    
    echo ""
}

# 使用者分析模式
show_user_analysis() {
    local start_date="$1"
    local end_date="$2"
    
    # 如果沒有結束日期，設定為開始日期
    if [[ -z "$end_date" ]]; then
        end_date="$start_date"
    fi
    
    echo "🔥 colab-gpu 1-4 各使用者平均 GPU 使用率分析"
    echo "=============================================="
    
    if [[ "$start_date" == "$end_date" ]]; then
        echo "📅 分析日期: $start_date"
    else
        echo "📅 分析期間: $start_date 至 $end_date"
    fi
    echo ""
    
    # 使用關聯陣列來儲存使用者統計
    declare -A user_gpu_sum
    declare -A user_vram_sum
    declare -A user_gpu_count
    declare -A user_vram_count
    declare -A user_active_gpus
    declare -A user_daily_total_gpu_usage
    declare -A user_valid_days
    
    local total_days=0
    local processed_days=0
    
    # 計算日期範圍內的總天數
    local current_date="$start_date"
    local date_count=0
    while [[ "$current_date" < "$end_date" ]] || [[ "$current_date" == "$end_date" ]]; do
        date_count=$((date_count + 1))
        current_date=$(date -d "$current_date + 1 day" "+%Y-%m-%d")
    done
    
    # 遍歷每一天，計算每日每個使用者的總GPU使用量
    current_date="$start_date"
    while [[ "$current_date" < "$end_date" ]] || [[ "$current_date" == "$end_date" ]]; do
        total_days=$((total_days + 1))
        
        # 每日每個使用者的GPU使用量統計
        declare -A daily_user_gpu_usage
        local daily_has_data=false
        
        # 遍歷所有節點
        for node in "${COLAB_NODES[@]}"; do
            local node_dir="$DATA_DIR/$node"
            local date_dir="$node_dir/$current_date"
            local avg_file="$date_dir/average_$current_date.csv"
            
            if [[ -f "$avg_file" ]]; then
                daily_has_data=true
                
                # 讀取該節點該日的數據
                while IFS=',' read -r gpu_idx gpu_util vram_util user || [[ -n "$gpu_idx" ]]; do
                    # 跳過標題行和總平均行
                    if [[ "$gpu_idx" =~ ^GPU\[[0-9]+\]$ ]] && [[ "$gpu_util" =~ ^[0-9]+\.?[0-9]*$ ]] && [[ "$vram_util" =~ ^[0-9]+\.?[0-9]*$ ]]; then
                        # 清理使用者名稱
                        user=$(echo "$user" | tr -d '\r\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
                        
                        # 跳過無效使用者
                        if [[ "$user" == "所有使用者" ]] || [[ -z "$user" ]]; then
                            continue
                        fi
                        
                        # 初始化使用者數據
                        if [[ -z "${user_gpu_sum[$user]}" ]]; then
                            user_gpu_sum[$user]=0
                            user_vram_sum[$user]=0
                            user_gpu_count[$user]=0
                            user_vram_count[$user]=0
                            user_active_gpus[$user]=0
                            user_daily_total_gpu_usage[$user]=0
                            user_valid_days[$user]=0
                        fi
                        
                        if [[ -z "${daily_user_gpu_usage[$user]}" ]]; then
                            daily_user_gpu_usage[$user]=0
                        fi
                        
                        # 累加總體統計
                        user_gpu_sum[$user]=$(awk "BEGIN {printf \"%.6f\", ${user_gpu_sum[$user]} + $gpu_util}")
                        user_vram_sum[$user]=$(awk "BEGIN {printf \"%.6f\", ${user_vram_sum[$user]} + $vram_util}")
                        user_gpu_count[$user]=$((${user_gpu_count[$user]} + 1))
                        user_vram_count[$user]=$((${user_vram_count[$user]} + 1))
                        
                        # 累加每日總GPU使用量
                        daily_user_gpu_usage[$user]=$(awk "BEGIN {printf \"%.6f\", ${daily_user_gpu_usage[$user]} + $gpu_util}")
                        
                        # 計算活躍GPU（使用率>1%）
                        if (( $(awk "BEGIN {print ($gpu_util > 1)}") )); then
                            user_active_gpus[$user]=$((${user_active_gpus[$user]} + 1))
                        fi
                    fi
                done < "$avg_file"
            fi
        done
        
        # 如果這一天有數據，更新每個使用者的每日總平均
        if [[ "$daily_has_data" == "true" ]]; then
            processed_days=$((processed_days + 1))
            
            for user in "${!daily_user_gpu_usage[@]}"; do
                user_daily_total_gpu_usage[$user]=$(awk "BEGIN {printf \"%.6f\", ${user_daily_total_gpu_usage[$user]} + ${daily_user_gpu_usage[$user]}}")
                user_valid_days[$user]=$((${user_valid_days[$user]} + 1))
            done
        fi
        
        # 移動到下一天
        current_date=$(date -d "$current_date + 1 day" "+%Y-%m-%d")
    done
    
    echo "📊 各使用者平均 GPU 使用率統計 (按每日總平均GPU使用量排序):"
    echo "使用者          GPU平均(%)  VRAM平均(%)  總GPU數  活躍GPU  活躍率  每日總平均GPU"
    echo "--------------------------------------------------------------------------------"
    
    # 創建帶有每日總平均GPU使用量的排序陣列
    declare -A user_daily_avg_gpu
    for user in "${!user_gpu_sum[@]}"; do
        local daily_avg="0.00"
        if [[ ${user_valid_days[$user]} -gt 0 ]]; then
            daily_avg=$(awk "BEGIN {printf \"%.2f\", ${user_daily_total_gpu_usage[$user]} / ${user_valid_days[$user]}}")
        fi
        user_daily_avg_gpu[$user]=$daily_avg
    done
    
    # 按每日總平均GPU使用量排序使用者（降序）
    for user in $(for u in "${!user_daily_avg_gpu[@]}"; do echo "${user_daily_avg_gpu[$u]} $u"; done | sort -nr | cut -d' ' -f2-); do
        local user_gpu_avg="0.00"
        local user_vram_avg="0.00"
        local total_gpus=${user_gpu_count[$user]}
        local active_gpus=${user_active_gpus[$user]}
        local active_rate="0.0"
        local daily_avg_gpu=${user_daily_avg_gpu[$user]}
        
        # 計算平均值
        if [[ $total_gpus -gt 0 ]]; then
            user_gpu_avg=$(awk "BEGIN {printf \"%.2f\", ${user_gpu_sum[$user]} / ${user_gpu_count[$user]}}")
            user_vram_avg=$(awk "BEGIN {printf \"%.2f\", ${user_vram_sum[$user]} / ${user_vram_count[$user]}}")
            active_rate=$(awk "BEGIN {printf \"%.1f\", ($active_gpus / $total_gpus) * 100}")
        fi
        
        # 格式化顯示使用者名稱（限制長度）
        local display_user="$user"
        if [[ ${#display_user} -gt 12 ]]; then
            display_user="${display_user:0:9}..."
        fi
        
        # 使用者狀態分析
        local status_emoji="💤"  # 預設：閒置
        if (( $(awk "BEGIN {print ($user_gpu_avg > 10)}") )); then
            status_emoji="🔥"  # 高使用率
        elif (( $(awk "BEGIN {print ($user_gpu_avg > 1)}") )); then
            status_emoji="⚡"  # 中等使用率
        elif [[ "$user" == "未使用" ]]; then
            status_emoji="💤"  # 未使用
        elif [[ "$user" == "admin" ]]; then
            status_emoji="👑"  # 管理員
        fi
        
        printf "%s %-12s %7s%%    %8s%%   %6d    %6d   %6s%%      %8s%%\n" \
               "$status_emoji" \
               "$display_user" \
               "$user_gpu_avg" \
               "$user_vram_avg" \
               "$total_gpus" \
               "$active_gpus" \
               "$active_rate" \
               "$daily_avg_gpu"
    done
    
    echo ""
    echo "🏆 每日總平均 GPU 使用量排名 TOP 5:"
    echo "排名  使用者          每日總平均GPU(%)  分析天數"
    echo "------------------------------------------------"
    
    local rank=1
    for user in $(for u in "${!user_daily_avg_gpu[@]}"; do echo "${user_daily_avg_gpu[$u]} $u"; done | sort -nr | head -5 | cut -d' ' -f2-); do
        local daily_avg=${user_daily_avg_gpu[$user]}
        local valid_days=${user_valid_days[$user]}
        local display_user="$user"
        if [[ ${#display_user} -gt 15 ]]; then
            display_user="${display_user:0:12}..."
        fi
        
        local medal=""
        case $rank in
            1) medal="🥇" ;;
            2) medal="🥈" ;;
            3) medal="🥉" ;;
            *) medal="  " ;;
        esac
        
        printf "%s %2d  %-15s      %10s%%       %3d\n" \
               "$medal" "$rank" "$display_user" "$daily_avg" "$valid_days"
        
        rank=$((rank + 1))
    done
    
    echo ""
    echo "📈 使用者統計總結:"
    
    # 計算總體統計
    local total_users=0
    local active_users=0
    local total_gpu_utilization=0
    local total_vram_utilization=0
    local total_active_gpus=0
    local total_gpus=0
    
    for user in "${!user_gpu_sum[@]}"; do
        if [[ "$user" != "未使用" ]]; then
            total_users=$((total_users + 1))
            
            local user_gpu_avg=$(awk "BEGIN {printf \"%.2f\", ${user_gpu_sum[$user]} / ${user_gpu_count[$user]}}")
            local user_vram_avg=$(awk "BEGIN {printf \"%.2f\", ${user_vram_sum[$user]} / ${user_vram_count[$user]}}")
            
            if (( $(awk "BEGIN {print ($user_gpu_avg > 1)}") )); then
                active_users=$((active_users + 1))
            fi
            
            total_gpu_utilization=$(awk "BEGIN {printf \"%.6f\", $total_gpu_utilization + $user_gpu_avg}")
            total_vram_utilization=$(awk "BEGIN {printf \"%.6f\", $total_vram_utilization + $user_vram_avg}")
            total_active_gpus=$((total_active_gpus + ${user_active_gpus[$user]}))
            total_gpus=$((total_gpus + ${user_gpu_count[$user]}))
        fi
    done
    
    if [[ $total_users -gt 0 ]]; then
        local avg_user_gpu=$(awk "BEGIN {printf \"%.2f\", $total_gpu_utilization / $total_users}")
        local avg_user_vram=$(awk "BEGIN {printf \"%.2f\", $total_vram_utilization / $total_users}")
        local overall_active_rate=$(awk "BEGIN {printf \"%.1f\", ($total_active_gpus / $total_gpus) * 100}")
        
        echo "  👥 總使用者數: $total_users (活躍使用者: $active_users)"
        echo "  📊 平均使用率: GPU ${avg_user_gpu}%, VRAM ${avg_user_vram}%"
        echo "  🔋 總體活躍率: ${overall_active_rate}% (${total_active_gpus}/${total_gpus} GPU)"
        
        # 資料完整度
        local data_completeness=$(awk "BEGIN {printf \"%.1f\", ($processed_days / $total_days) * 100}")
        echo "  📈 資料完整度: ${data_completeness}% (${processed_days}/${total_days} 節點×天數)"
    else
        echo "  ⚠️  沒有找到有效的使用者數據"
    fi
    
    echo ""
    
    # 使用模式說明
    echo "💡 圖示說明:"
    echo "  🔥 高使用率 (>10%)  ⚡ 中等使用率 (1-10%)  💤 低使用率 (<1%)"
    echo "  👑 管理員帳號       💤 未使用GPU"
    echo ""
}

# 趨勢分析模式
show_trend() {
    local start_date="$1"
    local end_date="$2"
    
    echo "🔥 colab-gpu 1-4 節點趨勢分析"
    echo "==============================="
    echo "📅 分析期間: $start_date 至 $end_date"
    echo ""
    
    echo "📈 每日總平均趨勢:"
    echo "日期          GPU平均(%)  VRAM平均(%)  活躍GPU  節點狀態"
    echo "-------------------------------------------------------"
    
    local range_gpu_sum=0
    local range_vram_sum=0
    local range_gpu_count=0
    local range_vram_count=0
    local valid_days=0
    
    local current_date="$start_date"
    while [[ "$current_date" != $(date -d "$end_date + 1 day" +%Y-%m-%d) ]]; do
        declare -A DAILY_NODE_STATS
        calculate_daily_node_stats "$current_date"
        
        if [[ $DAILY_ACTIVE_NODES -gt 0 ]]; then
            valid_days=$((valid_days + 1))
            range_gpu_sum=$(awk "BEGIN {print $range_gpu_sum + $DAILY_GPU_AVG}")
            range_vram_sum=$(awk "BEGIN {print $range_vram_sum + $DAILY_VRAM_AVG}")
            range_gpu_count=$((range_gpu_count + DAILY_GPU_COUNT))
            range_vram_count=$((range_vram_count + DAILY_VRAM_COUNT))
            
            # 計算當日活躍GPU
            local daily_active=0
            for node in "${COLAB_NODES[@]}"; do
                local active_key="${node}_active_gpus"
                if [[ -n "${DAILY_NODE_STATS[$active_key]}" ]]; then
                    daily_active=$((daily_active + ${DAILY_NODE_STATS[$active_key]}))
                fi
            done
            
            printf "%-12s  %8s     %8s      %2s/32    %s/4\n" \
                   "$current_date" "$DAILY_GPU_AVG" "$DAILY_VRAM_AVG" "$daily_active" "$DAILY_ACTIVE_NODES"
        else
            printf "%-12s  %8s     %8s      %2s      %s\n" \
                   "$current_date" "無資料" "無資料" "--" "0/4"
        fi
        
        current_date=$(date -d "$current_date + 1 day" +%Y-%m-%d)
    done
    
    echo ""
    
    if [[ $valid_days -gt 0 ]]; then
        local period_gpu_avg=$(awk "BEGIN {printf \"%.2f\", $range_gpu_sum / $valid_days}")
        local period_vram_avg=$(awk "BEGIN {printf \"%.2f\", $range_vram_sum / $valid_days}")
        
        echo "🎯 期間總結:"
        echo "  📊 期間GPU平均:   ${period_gpu_avg}%"
        echo "  💾 期間VRAM平均:  ${period_vram_avg}%"
        echo "  📅 有效資料天數:  ${valid_days} 天"
        echo "  🔋 平均GPU數量:   $(awk "BEGIN {printf \"%.0f\", $range_gpu_count / $valid_days}") 個/天"
    fi
    echo ""
}

# CSV匯出模式
export_csv() {
    local start_date="$1"
    local end_date="$2"
    local output_file="colab_gpu_stats_${start_date}_to_${end_date}.csv"
    
    echo "🔥 匯出 colab-gpu 1-4 節點統計數據"
    echo "===================================="
    echo "📅 期間: $start_date 至 $end_date"
    echo "📄 輸出檔案: $output_file"
    echo ""
    
    # 創建CSV標題
    echo "日期,GPU總平均(%),VRAM總平均(%),活躍節點數,colab-gpu1_GPU,colab-gpu1_VRAM,colab-gpu2_GPU,colab-gpu2_VRAM,colab-gpu3_GPU,colab-gpu3_VRAM,colab-gpu4_GPU,colab-gpu4_VRAM" > "$output_file"
    
    local current_date="$start_date"
    while [[ "$current_date" != $(date -d "$end_date + 1 day" +%Y-%m-%d) ]]; do
        declare -A DAILY_NODE_STATS
        calculate_daily_node_stats "$current_date"
        
        # 準備CSV行數據
        local csv_line="$current_date,$DAILY_GPU_AVG,$DAILY_VRAM_AVG,$DAILY_ACTIVE_NODES"
        
        for node in "${COLAB_NODES[@]}"; do
            local gpu_avg="${DAILY_NODE_STATS[${node}_gpu_avg]:-0.00}"
            local vram_avg="${DAILY_NODE_STATS[${node}_vram_avg]:-0.00}"
            csv_line="$csv_line,$gpu_avg,$vram_avg"
        done
        
        echo "$csv_line" >> "$output_file"
        current_date=$(date -d "$current_date + 1 day" +%Y-%m-%d)
    done
    
    print_success "CSV 檔案已匯出: $output_file"
    echo ""
}

# 主程式
main() {
    local mode="${1:-summary}"
    local start_date=""
    local end_date=""
    
    # 處理參數
    case "$mode" in
        "help"|"-h"|"--help")
            show_usage
            exit 0
            ;;
        "summary"|"s"|"detailed"|"d")
            if [[ -n "$2" ]]; then
                start_date="$2"
                end_date="$2"
            fi
            ;;
        "individual"|"i"|"user"|"u"|"trend"|"t"|"export"|"e")
            if [[ -n "$2" && -n "$3" ]]; then
                start_date="$2"
                end_date="$3"
            elif [[ -n "$2" ]]; then
                start_date="$2"
                end_date="$2"
            fi
            ;;
        *)
            # 如果第一個參數是日期格式，當作日期處理
            if [[ "$1" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
                mode="summary"
                start_date="$1"
                end_date="${2:-$1}"
            else
                print_error "未知的模式: $mode"
                show_usage
                exit 1
            fi
            ;;
    esac
    
    # 如果沒有指定日期，使用最新資料
    if [[ -z "$start_date" ]]; then
        start_date=$(find_latest_data_date)
        end_date="$start_date"
        
        if [[ -z "$start_date" ]]; then
            print_error "找不到任何 colab-gpu 節點的資料"
            exit 1
        fi
        
        print_info "自動選擇最新資料日期: $start_date"
        echo ""
    fi
    
    # 驗證日期
    validate_date "$start_date"
    validate_date "$end_date"
    
    if [[ "$start_date" > "$end_date" ]]; then
        print_error "開始日期不能晚於結束日期"
        exit 1
    fi
    
    # 檢查資料目錄
    if [[ ! -d "$DATA_DIR" ]]; then
        print_error "找不到資料目錄: $DATA_DIR"
        exit 1
    fi
    
    # 執行對應模式
    case "$mode" in
        "summary"|"s")
            show_summary "$start_date"
            ;;
        "detailed"|"d")
            show_detailed "$start_date"
            ;;
        "individual"|"i")
            show_individual "$start_date" "$end_date"
            ;;
        "user"|"u")
            show_user_analysis "$start_date" "$end_date"
            ;;
        "trend"|"t")
            show_trend "$start_date" "$end_date"
            ;;
        "export"|"e")
            export_csv "$start_date" "$end_date"
            ;;
    esac
}

# 執行主程式
main "$@"