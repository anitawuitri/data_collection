#!/bin/bash

# Batch collect user information from 11-05 to 11-19
# This script will re-collect data with user information for the specified date range

start_date="2025-11-05"
end_date="2025-11-19"

echo "🔥 批量收集使用者資訊：從 $start_date 到 $end_date"
echo "這將重新收集資料並加入使用者資訊"
echo ""

# 確保腳本有執行權限
chmod +x scripts/daily_gpu_log_with_users.sh

# 計算日期範圍
current_date="$start_date"
total_days=0
success_count=0

while [[ "$current_date" < "$end_date" ]] || [[ "$current_date" == "$end_date" ]]; do
    total_days=$((total_days + 1))
    current_date=$(date -d "$current_date + 1 day" "+%Y-%m-%d")
done

echo "總共需要處理 $total_days 天的資料"
echo ""

# 重置計數器
current_date="$start_date"

while [[ "$current_date" < "$end_date" ]] || [[ "$current_date" == "$end_date" ]]; do
    echo "==============================================="
    echo "📅 處理日期: $current_date"
    echo "==============================================="
    
    # 執行資料收集
    if ./scripts/daily_gpu_log_with_users.sh "$current_date"; then
        success_count=$((success_count + 1))
        echo "✅ $current_date 資料收集完成"
    else
        echo "❌ $current_date 資料收集失敗"
    fi
    
    echo ""
    
    # 移動到下一天
    current_date=$(date -d "$current_date + 1 day" "+%Y-%m-%d")
    
    # 短暫暫停避免 API 負載過重
    sleep 1
done

echo "==============================================="
echo "📊 批量收集完成統計"
echo "==============================================="
echo "總處理天數: $total_days"
echo "成功天數: $success_count"
echo "失敗天數: $((total_days - success_count))"

if [ $success_count -eq $total_days ]; then
    echo "🎉 所有資料收集成功！"
else
    echo "⚠️ 有部分資料收集失敗，請檢查錯誤訊息"
fi

echo ""
echo "💡 現在可以使用以下命令分析使用者資訊："
echo "   ./colab_gpu_stats.sh user $start_date $end_date"
echo "   ./colab_gpu_stats.sh individual $start_date $end_date"
echo "   ./colab_gpu_stats.sh trend $start_date $end_date"