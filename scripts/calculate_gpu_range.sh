#!/bin/bash

# 顯示使用方法
usage() {
    echo "使用方法: $0 開始日期 結束日期 [特定 GPU ID]"
    echo "日期格式: YYYY-MM-DD (例如: 2025-05-22)"
    echo "若提供特定 GPU ID，則只計算該 GPU 的平均使用率"
    echo "範例:"
    echo "  $0 2025-05-01 2025-05-15        # 計算所有 GPU 在5/1至5/15期間的平均使用率"
    echo "  $0 2025-05-01 2025-05-15 1      # 只計算 GPU 1 在5/1至5/15期間的平均使用率"
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
SPECIFIC_GPU="$3"

validate_date "$START_DATE"
validate_date "$END_DATE"

# 檢查開始日期是否小於等於結束日期
if [[ $(date -d "$START_DATE" +%s) -gt $(date -d "$END_DATE" +%s) ]]; then
    echo "錯誤: 開始日期必須早於或等於結束日期"
    exit 1
fi

echo "計算 $START_DATE 至 $END_DATE 的 GPU 平均使用率..."

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
RESULT_FILE="${RESULT_DIR}/gpu_usage_${START_DATE}_to_${END_DATE}.csv"
SUMMARY_FILE="${RESULT_DIR}/gpu_summary_${START_DATE}_to_${END_DATE}.txt"

# 初始化結果檔案
echo "主機,GPU,日期,平均使用率(%)" > "$RESULT_FILE"
echo "" > "$SUMMARY_FILE"

# 統計變數
declare -A HOST_GPU_TOTALS  # 每個主機每個GPU的總和
declare -A HOST_GPU_COUNTS  # 每個主機每個GPU的計數
declare -A ALL_GPU_TOTALS   # 所有主機每個GPU的總和
declare -A ALL_GPU_COUNTS   # 所有主機每個GPU的計數
TOTAL_SUM=0
TOTAL_COUNT=0

# 處理每個主機
for HOST in "${COLAB_HOSTS[@]}"; do
    echo "處理主機: $HOST"
    
    # 處理每個日期
    for DATE in "${DATES[@]}"; do
        echo "  檢查日期: $DATE"
        
        # 處理每個 GPU
        for GPU_ID in "${GPU_IDS[@]}"; do
            # 如果指定了特定 GPU，則只處理該 GPU
            if [ -n "$SPECIFIC_GPU" ] && [ "$GPU_ID" != "$SPECIFIC_GPU" ]; then
                continue
            fi
            
            # 檢查平均使用率檔案
            AVG_FILE="${DATA_DIR}/${HOST}/${DATE}/average_${DATE}.csv"
            
            if [ -f "$AVG_FILE" ]; then
                # 從平均檔案中提取指定 GPU 的使用率
                GPU_USAGE=$(grep "^gpu${GPU_ID}," "$AVG_FILE" | cut -d',' -f2)
                
                # 檢查是否找到使用率且不是 N/A
                if [ -n "$GPU_USAGE" ] && [ "$GPU_USAGE" != "N/A" ]; then
                    echo "$HOST,$GPU_ID,$DATE,$GPU_USAGE" >> "$RESULT_FILE"
                    
                    # 更新統計資料
                    HOST_GPU_KEY="${HOST}_${GPU_ID}"
                    HOST_GPU_TOTALS[$HOST_GPU_KEY]=$(echo "${HOST_GPU_TOTALS[$HOST_GPU_KEY]:-0} + $GPU_USAGE" | bc)
                    HOST_GPU_COUNTS[$HOST_GPU_KEY]=$((${HOST_GPU_COUNTS[$HOST_GPU_KEY]:-0} + 1))
                    
                    ALL_GPU_TOTALS[$GPU_ID]=$(echo "${ALL_GPU_TOTALS[$GPU_ID]:-0} + $GPU_USAGE" | bc)
                    ALL_GPU_COUNTS[$GPU_ID]=$((${ALL_GPU_COUNTS[$GPU_ID]:-0} + 1))
                    
                    TOTAL_SUM=$(echo "$TOTAL_SUM + $GPU_USAGE" | bc)
                    TOTAL_COUNT=$((TOTAL_COUNT + 1))
                fi
            else
                echo "    警告: 找不到 $AVG_FILE"
            fi
        done
    done
done

# 生成摘要報告
{
    echo "=================================="
    echo "GPU 使用率統計報告"
    echo "期間: $START_DATE 至 $END_DATE"
    echo "=================================="
    echo ""
    
    # 如果指定了特定 GPU，只顯示該 GPU 的統計資料
    if [ -n "$SPECIFIC_GPU" ]; then
        echo "僅顯示 GPU $SPECIFIC_GPU 的統計資料"
        echo ""
    fi
    
    echo "== 依主機與 GPU 的平均使用率 =="
    for HOST in "${COLAB_HOSTS[@]}"; do
        echo "主機: $HOST"
        for GPU_ID in "${GPU_IDS[@]}"; do
            # 如果指定了特定 GPU，則只處理該 GPU
            if [ -n "$SPECIFIC_GPU" ] && [ "$GPU_ID" != "$SPECIFIC_GPU" ]; then
                continue
            fi
            
            HOST_GPU_KEY="${HOST}_${GPU_ID}"
            if [ "${HOST_GPU_COUNTS[$HOST_GPU_KEY]:-0}" -gt 0 ]; then
                AVG=$(echo "scale=2; ${HOST_GPU_TOTALS[$HOST_GPU_KEY]} / ${HOST_GPU_COUNTS[$HOST_GPU_KEY]}" | bc)
                echo "  GPU $GPU_ID: $AVG%"
            else
                echo "  GPU $GPU_ID: 無資料"
            fi
        done
        echo ""
    done
    
    echo "== 各 GPU 的整體平均使用率 =="
    for GPU_ID in "${GPU_IDS[@]}"; do
        # 如果指定了特定 GPU，則只處理該 GPU
        if [ -n "$SPECIFIC_GPU" ] && [ "$GPU_ID" != "$SPECIFIC_GPU" ]; then
            continue
        fi
        
        if [ "${ALL_GPU_COUNTS[$GPU_ID]:-0}" -gt 0 ]; then
            AVG=$(echo "scale=2; ${ALL_GPU_TOTALS[$GPU_ID]} / ${ALL_GPU_COUNTS[$GPU_ID]}" | bc)
            echo "GPU $GPU_ID: $AVG%"
        else
            echo "GPU $GPU_ID: 無資料"
        fi
    done
    
    echo ""
    echo "== 總體平均使用率 =="
    if [ "$TOTAL_COUNT" -gt 0 ]; then
        OVERALL_AVG=$(echo "scale=2; $TOTAL_SUM / $TOTAL_COUNT" | bc)
        echo "總體平均: $OVERALL_AVG%"
    else
        echo "總體平均: 無資料"
    fi
    
    echo ""
    echo "詳細數據已保存至: $RESULT_FILE"
} > "$SUMMARY_FILE"

echo "已完成分析，摘要報告保存至: $SUMMARY_FILE"
echo "詳細數據保存至: $RESULT_FILE"

# 顯示摘要報告
cat "$SUMMARY_FILE"
