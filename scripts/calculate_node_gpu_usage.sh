#!/bin/bash

# 顯示使用方法
usage() {
    echo "使用方法: $0 開始日期 結束日期 [節點名稱]"
    echo "日期格式: YYYY-MM-DD (例如: 2025-05-22)"
    echo "若提供節點名稱，則只計算該節點的平均使用率"
    echo "範例:"
    echo "  $0 2025-05-01 2025-05-15         # 計算所有節點在5/1至5/15期間的平均使用率"
    echo "  $0 2025-05-01 2025-05-15 colab-gpu1  # 只計算 colab-gpu1 在5/1至5/15期間的平均使用率"
    exit 1
}

# 日期格式驗證函數
validate_date() {
    local date_str=$1
    # 檢查日期格式是否符合 YYYY-MM-DD
    if ! [[ $date_str =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
        echo "錯誤: 日期格式不正確 ($date_str)，應為 YYYY-MM-DD"
        usage
    fi
    # 進一步驗證日期是否有效
    if ! date -d "$date_str" > /dev/null 2>&1; then
        echo "錯誤: 無效的日期 ($date_str)"
        usage
    fi
}

# 檢查參數數量
if [ "$#" -lt 2 ]; then
    echo "錯誤: 缺少必要參數"
    usage
fi

# 解析並驗證日期
START_DATE="$1"
END_DATE="$2"
SPECIFIC_NODE="$3"

validate_date "$START_DATE"
validate_date "$END_DATE"

# 檢查開始日期是否小於等於結束日期
if [[ $(date -d "$START_DATE" +%s) -gt $(date -d "$END_DATE" +%s) ]]; then
    echo "錯誤: 開始日期必須早於或等於結束日期"
    exit 1
fi

echo "計算 $START_DATE 至 $END_DATE 的節點 GPU 平均使用率..."

# 固定 GPU ID 列表 (與 daily_gpu_log.sh 一致)
GPU_IDS=(1 9 17 25 33 41 49 57)

# 主機列表
COLAB_HOSTS=("colab-gpu1" "colab-gpu2" "colab-gpu3" "colab-gpu4")

# 目錄前綴
DATA_DIR="./data"

# 生成日期範圍
CURRENT_DATE="$START_DATE"
DATES=()
while [[ $(date -d "$CURRENT_DATE" +%s) -le $(date -d "$END_DATE" +%s) ]]; do
    DATES+=("$CURRENT_DATE")
    CURRENT_DATE=$(date -d "$CURRENT_DATE + 1 day" +%Y-%m-%d)
done

echo "分析日期範圍: ${DATES[@]}"

# 準備結果目錄
RESULT_DIR="${DATA_DIR}/reports"
mkdir -p "$RESULT_DIR"
RESULT_FILE="${RESULT_DIR}/node_gpu_usage_${START_DATE}_to_${END_DATE}.csv"
SUMMARY_FILE="${RESULT_DIR}/node_gpu_summary_${START_DATE}_to_${END_DATE}.txt"

# 初始化結果檔案
echo "節點,日期,平均使用率(%),平均VRAM使用率(%)" > "$RESULT_FILE"
echo "" > "$SUMMARY_FILE"

# 統計變數
declare -A NODE_DAILY_TOTALS  # 每個節點每天的總和
declare -A NODE_DAILY_COUNTS  # 每個節點每天的計數
declare -A NODE_TOTALS       # 每個節點的總和
declare -A NODE_COUNTS       # 每個節點的計數
declare -A GPU_NODE_TOTALS   # 每個節點每個GPU的總和
declare -A GPU_NODE_COUNTS   # 每個節點每個GPU的計數
declare -A NODE_DAILY_VRAM_TOTALS  # 每個節點每天的VRAM總和
declare -A NODE_VRAM_TOTALS       # 每個節點的VRAM總和
declare -A GPU_NODE_VRAM_TOTALS   # 每個節點每個GPU的VRAM總和
TOTAL_SUM=0
TOTAL_COUNT=0
TOTAL_VRAM_SUM=0

# 處理每個節點
for HOST in "${COLAB_HOSTS[@]}"; do
    # 如果指定了特定節點，則只處理該節點
    if [ -n "$SPECIFIC_NODE" ] && [ "$HOST" != "$SPECIFIC_NODE" ]; then
        continue
    fi

    echo "處理節點: $HOST"
    NODE_TOTALS[$HOST]=0
    NODE_COUNTS[$HOST]=0
    NODE_VRAM_TOTALS[$HOST]=0
    
    # 處理每個日期
    for DATE in "${DATES[@]}"; do
        echo "  檢查日期: $DATE"
        NODE_DAILY_TOTALS["${HOST}_${DATE}"]=0
        NODE_DAILY_COUNTS["${HOST}_${DATE}"]=0
        NODE_DAILY_VRAM_TOTALS["${HOST}_${DATE}"]=0
        
        # 查找該日期的平均使用率檔案，計算所有 GPU 的平均
        HOST_DIR="${DATA_DIR}/${HOST}/${DATE}"
        if [ -d "$HOST_DIR" ]; then
            for GPU_ID in "${GPU_IDS[@]}"; do
                # 查找 CSV 檔案
                CSV_FILE="${HOST_DIR}/gpu${GPU_ID}_${DATE}.csv"
                if [ -f "$CSV_FILE" ]; then
                    # 計算此 GPU 的平均使用率
                    GPU_AVG=$(awk -F, 'NR>1 {sum+=$3; count++} END {if(count>0) print sum/count; else print "N/A"}' "$CSV_FILE")
                    
                    # 計算此 GPU 的平均 VRAM 使用率 (第四欄)
                    VRAM_AVG=$(awk -F, 'NR>1 {sum+=$4; count++} END {if(count>0) print sum/count; else print "N/A"}' "$CSV_FILE")
                    
                    # 確認數值有效
                    if [ "$GPU_AVG" != "N/A" ] && [ "$GPU_AVG" != "" ]; then
                        NODE_DAILY_TOTALS["${HOST}_${DATE}"]=$(echo "${NODE_DAILY_TOTALS["${HOST}_${DATE}"]} + $GPU_AVG" | bc)
                        NODE_DAILY_COUNTS["${HOST}_${DATE}"]=$((${NODE_DAILY_COUNTS["${HOST}_${DATE}"]} + 1))
                        
                        # 記錄每個 GPU 在每個節點的使用率總和和計數
                        GPU_NODE_KEY="${HOST}_${GPU_ID}"
                        GPU_NODE_TOTALS[$GPU_NODE_KEY]=$(echo "${GPU_NODE_TOTALS[$GPU_NODE_KEY]:-0} + $GPU_AVG" | bc)
                        GPU_NODE_COUNTS[$GPU_NODE_KEY]=$((${GPU_NODE_COUNTS[$GPU_NODE_KEY]:-0} + 1))
                    fi
                    
                    # 處理 VRAM 使用率數據
                    if [ "$VRAM_AVG" != "N/A" ] && [ "$VRAM_AVG" != "" ]; then
                        NODE_DAILY_VRAM_TOTALS["${HOST}_${DATE}"]=$(echo "${NODE_DAILY_VRAM_TOTALS["${HOST}_${DATE}"]} + $VRAM_AVG" | bc)
                        # 記錄每個 GPU 在每個節點的 VRAM 使用率總和
                        GPU_NODE_KEY="${HOST}_${GPU_ID}"
                        GPU_NODE_VRAM_TOTALS[$GPU_NODE_KEY]=$(echo "${GPU_NODE_VRAM_TOTALS[$GPU_NODE_KEY]:-0} + $VRAM_AVG" | bc)
                    fi
                fi
            done
            
            # 計算此節點此日期的平均值
            if [ "${NODE_DAILY_COUNTS["${HOST}_${DATE}"]}" -gt 0 ]; then
                # 使用 awk 確保數值格式正確 (總是有小數點前的數字)
                DAILY_AVG=$(echo "scale=6; ${NODE_DAILY_TOTALS["${HOST}_${DATE}"]} / ${NODE_DAILY_COUNTS["${HOST}_${DATE}"]}" | bc)
                DAILY_VRAM_AVG=$(echo "scale=6; ${NODE_DAILY_VRAM_TOTALS["${HOST}_${DATE}"]} / ${NODE_DAILY_COUNTS["${HOST}_${DATE}"]}" | bc)
                # 修正數值格式，確保小數點前有數字
                FORMATTED_AVG=$(awk -v avg="$DAILY_AVG" 'BEGIN {printf "%.2f", avg}')
                FORMATTED_VRAM_AVG=$(awk -v avg="$DAILY_VRAM_AVG" 'BEGIN {printf "%.2f", avg}')
                echo "$HOST,$DATE,$FORMATTED_AVG,$FORMATTED_VRAM_AVG" >> "$RESULT_FILE"
                
                # 取得格式化後的數值
                RAW_VAL=$(echo "$FORMATTED_AVG" | sed 's/,/./g')
                RAW_VRAM_VAL=$(echo "$FORMATTED_VRAM_AVG" | sed 's/,/./g')
                
                # 更新節點總計 (使用格式化的數值確保一致性)
                NODE_TOTALS[$HOST]=$(echo "${NODE_TOTALS[$HOST]} + $RAW_VAL" | bc)
                NODE_COUNTS[$HOST]=$((${NODE_COUNTS[$HOST]} + 1))
                NODE_VRAM_TOTALS[$HOST]=$(echo "${NODE_VRAM_TOTALS[$HOST]} + $RAW_VRAM_VAL" | bc)
                
                # 更新總計 - 使用相同的格式化數值
                TOTAL_SUM=$(echo "$TOTAL_SUM + $RAW_VAL" | bc)
                TOTAL_COUNT=$((TOTAL_COUNT + 1))
                TOTAL_VRAM_SUM=$(echo "$TOTAL_VRAM_SUM + $RAW_VRAM_VAL" | bc)
                
                # 為了顯示目的，使用格式化的數值
                echo "    $HOST 在 $DATE 的平均使用率: $FORMATTED_AVG%, 平均VRAM使用率: $FORMATTED_VRAM_AVG%"
            else
                echo "    $HOST 在 $DATE 無有效數據"
            fi
        else
            echo "    警告: 找不到目錄 $HOST_DIR"
        fi
    done
    
    # 計算此節點的總平均值
    if [ "${NODE_COUNTS[$HOST]}" -gt 0 ]; then
        NODE_AVG=$(echo "scale=6; ${NODE_TOTALS[$HOST]} / ${NODE_COUNTS[$HOST]}" | bc)
        NODE_VRAM_AVG=$(echo "scale=6; ${NODE_VRAM_TOTALS[$HOST]} / ${NODE_COUNTS[$HOST]}" | bc)
        # 格式化數值
        FORMATTED_NODE_AVG=$(awk -v avg="$NODE_AVG" 'BEGIN {printf "%.2f", avg}')
        FORMATTED_NODE_VRAM_AVG=$(awk -v avg="$NODE_VRAM_AVG" 'BEGIN {printf "%.2f", avg}')
        echo "  $HOST 在整個期間的平均使用率: $FORMATTED_NODE_AVG%, 平均VRAM使用率: $FORMATTED_NODE_VRAM_AVG%"
    else
        echo "  $HOST 在整個期間無有效數據"
    fi
done

# 生成摘要報告
{
    echo "=================================="
    echo "節點 GPU 使用率統計報告"
    echo "期間: $START_DATE 至 $END_DATE"
    echo "=================================="
    echo ""
    
    # 如果指定了特定節點，只顯示該節點的統計資料
    if [ -n "$SPECIFIC_NODE" ]; then
        echo "僅顯示節點 $SPECIFIC_NODE 的統計資料"
        echo ""
    fi
    
    echo "== 各節點的平均 GPU 與 VRAM 使用率 =="
    for HOST in "${COLAB_HOSTS[@]}"; do
        # 如果指定了特定節點，則只處理該節點
        if [ -n "$SPECIFIC_NODE" ] && [ "$HOST" != "$SPECIFIC_NODE" ]; then
            continue
        fi
        
        # 直接從 CSV 檔案計算該節點的平均值
        NODE_AVG=$(awk -F, -v host="$HOST" 'NR>1 && $1==host {sum+=$3; count++} END {if(count>0) printf "%.2f", sum/count; else print "0.00"}' "$RESULT_FILE")
        NODE_VRAM_AVG=$(awk -F, -v host="$HOST" 'NR>1 && $1==host {sum+=$4; count++} END {if(count>0) printf "%.2f", sum/count; else print "0.00"}' "$RESULT_FILE")
        
        echo "節點 $HOST: GPU使用率 $NODE_AVG%, VRAM使用率 $NODE_VRAM_AVG%"
        
        # 顯示此節點下每個 GPU 的平均使用率與 VRAM 使用率
        echo "  各 GPU 平均使用率與 VRAM 使用率:"
        for GPU_ID in "${GPU_IDS[@]}"; do
            GPU_NODE_KEY="${HOST}_${GPU_ID}"
            if [ "${GPU_NODE_COUNTS[$GPU_NODE_KEY]:-0}" -gt 0 ]; then
                GPU_AVG=$(echo "scale=6; ${GPU_NODE_TOTALS[$GPU_NODE_KEY]} / ${GPU_NODE_COUNTS[$GPU_NODE_KEY]}" | bc)
                GPU_VRAM_AVG=$(echo "scale=6; ${GPU_NODE_VRAM_TOTALS[$GPU_NODE_KEY]:-0} / ${GPU_NODE_COUNTS[$GPU_NODE_KEY]}" | bc)
                # 格式化數值
                FORMATTED_GPU_AVG=$(awk -v avg="$GPU_AVG" 'BEGIN {printf "%.2f", avg}')
                FORMATTED_GPU_VRAM_AVG=$(awk -v avg="$GPU_VRAM_AVG" 'BEGIN {printf "%.2f", avg}')
                echo "    GPU $GPU_ID: GPU使用率 $FORMATTED_GPU_AVG%, VRAM使用率 $FORMATTED_GPU_VRAM_AVG%"
            else
                echo "    GPU $GPU_ID: 無資料"
            fi
        done
    done
    
    echo ""
    echo "== 總體平均使用率 =="
    if [ "$TOTAL_COUNT" -gt 0 ]; then
        # 從 CSV 文件中直接計算平均值，以確保準確性
        OVERALL_AVG=$(awk -F, 'NR>1 {sum+=$3; count++} END {if(count>0) printf "%.2f", sum/count; else print "0.00"}' "$RESULT_FILE")
        OVERALL_VRAM_AVG=$(awk -F, 'NR>1 {sum+=$4; count++} END {if(count>0) printf "%.2f", sum/count; else print "0.00"}' "$RESULT_FILE")
        
        echo "所有節點的平均 GPU 使用率: $OVERALL_AVG%"
        echo "所有節點的平均 VRAM 使用率: $OVERALL_VRAM_AVG%"
    else
        echo "所有節點的平均: 無資料"
    fi
    
    echo ""
    echo "== 各節點每日平均 GPU 使用率 =="
    for HOST in "${COLAB_HOSTS[@]}"; do
        # 如果指定了特定節點，則只處理該節點
        if [ -n "$SPECIFIC_NODE" ] && [ "$HOST" != "$SPECIFIC_NODE" ]; then
            continue
        fi
        
        echo "節點: $HOST"
        for DATE in "${DATES[@]}"; do
            if [ "${NODE_DAILY_COUNTS["${HOST}_${DATE}"]:-0}" -gt 0 ]; then
                DAILY_AVG=$(echo "scale=6; ${NODE_DAILY_TOTALS["${HOST}_${DATE}"]} / ${NODE_DAILY_COUNTS["${HOST}_${DATE}"]}" | bc)
                DAILY_VRAM_AVG=$(echo "scale=6; ${NODE_DAILY_VRAM_TOTALS["${HOST}_${DATE}"]} / ${NODE_DAILY_COUNTS["${HOST}_${DATE}"]}" | bc)
                # 格式化數值
                FORMATTED_DAILY_AVG=$(awk -v avg="$DAILY_AVG" 'BEGIN {printf "%.2f", avg}')
                FORMATTED_DAILY_VRAM_AVG=$(awk -v avg="$DAILY_VRAM_AVG" 'BEGIN {printf "%.2f", avg}')
                echo "  $DATE: GPU使用率 $FORMATTED_DAILY_AVG%, VRAM使用率 $FORMATTED_DAILY_VRAM_AVG%"
            else
                echo "  $DATE: 無資料"
            fi
        done
        echo ""
    done
    
    echo "詳細數據已保存至: $RESULT_FILE"
} > "$SUMMARY_FILE"

echo "已完成分析，摘要報告保存至: $SUMMARY_FILE"
echo "詳細數據保存至: $RESULT_FILE"

# 顯示摘要報告
cat "$SUMMARY_FILE"
