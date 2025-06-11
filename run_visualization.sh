#!/bin/bash

# GPU 使用率趨勢視覺化執行腳本
# 此腳本提供簡易的命令列介面來生成 GPU 使用率趨勢圖

set -e

# 設定腳本路徑
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR/scripts"
DATA_DIR="$SCRIPT_DIR/data"
PLOTS_DIR="$SCRIPT_DIR/plots"

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

print_warning() {
    echo -e "\033[1;33m[WARNING]\033[0m $1"
}

echo "=== AMD GPU 使用率視覺化工具 ==="
echo ""

# 檢查 Python 是否存在
if ! command -v python3 &> /dev/null; then
    echo "錯誤: 未找到 Python3，請先安裝 Python3"
    exit 1
fi

# 設定 Python 命令
PYTHON_CMD="python3"

# 檢查是否有虛擬環境
if [ -f "./.venv/bin/python" ]; then
    echo "使用虛擬環境..."
    PYTHON_CMD="./.venv/bin/python"
elif [ -f "./gpu_venv/bin/python" ]; then
    echo "使用 gpu_venv 虛擬環境..."
    PYTHON_CMD="./gpu_venv/bin/python"
fi

# 檢查並安裝依賴
echo "檢查 Python 依賴套件..."
if ! $PYTHON_CMD -c "import pandas, matplotlib, numpy, seaborn" &> /dev/null; then
    echo "安裝所需的 Python 套件..."
    
    # 如果使用虛擬環境，直接用 pip 安裝
    if [[ "$PYTHON_CMD" == *".venv"* ]] || [[ "$PYTHON_CMD" == *"gpu_venv"* ]]; then
        ${PYTHON_CMD%/python}/pip install pandas matplotlib numpy seaborn
    else
        # 嘗試其他安裝方式
        if pip3 install pandas matplotlib numpy seaborn --user &> /dev/null; then
            echo "使用 --user 模式安裝成功"
        elif pip3 install pandas matplotlib numpy seaborn --break-system-packages &> /dev/null; then
            echo "使用 --break-system-packages 模式安裝成功"
        else
            echo "提示: 無法自動安裝依賴套件，請手動執行下列其中一項："
            echo "1. pip3 install pandas matplotlib numpy seaborn --user"
            echo "2. pip3 install pandas matplotlib numpy seaborn --break-system-packages"
            echo "3. sudo apt install python3-pandas python3-matplotlib python3-numpy python3-seaborn"
            echo ""
            echo "或者創建虛擬環境："
            echo "   python3 -m venv gpu_venv"
            echo "   source gpu_venv/bin/activate"
            echo "   pip install pandas matplotlib numpy seaborn"
            echo ""
            echo "仍然嘗試執行（可能會失敗）..."
        fi
    fi
fi

echo "依賴套件檢查完成！"
echo ""

# 檢查數據目錄
if [ ! -d "./data" ]; then
    echo "錯誤: 未找到數據目錄 ./data"
    echo "請確保在專案根目錄執行此腳本"
    exit 1
fi

# 獲取可用的日期範圍
echo "檢查可用的數據..."
available_dates=$(find ./data/colab-gpu* -maxdepth 1 -type d -name "20*" | head -10 | sort | sed 's/.*\///')
if [ -z "$available_dates" ]; then
    echo "錯誤: 未找到任何數據"
    exit 1
fi

# 取得第一個和最後一個日期
start_date=$(echo "$available_dates" | head -1)
end_date=$(echo "$available_dates" | tail -1)

echo "找到數據日期範圍: $start_date 至 $end_date"
echo ""

# 創建輸出目錄
mkdir -p ./plots

# 創建簡化的 Python 腳本
cat > ./generate_plots.py << 'EOF'
#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import os
import sys
from datetime import datetime

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

def generate_node_comparison(start_date, end_date):
    """生成節點對比圖"""
    nodes = ['colab-gpu1', 'colab-gpu2', 'colab-gpu3', 'colab-gpu4']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    fig, ax = plt.subplots(figsize=(15, 8))
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    for i, node in enumerate(nodes):
        node_data = []
        node_dates = []
        
        for date in dates:
            date_str = date.strftime('%Y-%m-%d')
            avg_file = f"./data/{node}/{date_str}/average_{date_str}.csv"
            
            if os.path.exists(avg_file):
                try:
                    df = pd.read_csv(avg_file, encoding='utf-8')
                    if len(df.columns) >= 2:
                        df.columns = ['gpu', 'usage']
                        gpu_data = df[~df['gpu'].str.contains('全部平均', na=False)]
                        avg_usage = pd.to_numeric(gpu_data['usage'], errors='coerce').mean()
                        
                        if not np.isnan(avg_usage):
                            node_data.append(avg_usage)
                            node_dates.append(date)
                except:
                    continue
        
        if node_data:
            ax.plot(node_dates, node_data, label=node, marker='o', 
                   linewidth=2, markersize=6, color=colors[i])
    
    ax.set_title(f'各節點 GPU 平均使用率趨勢 ({start_date} 至 {end_date})', 
                fontsize=16, fontweight='bold')
    ax.set_xlabel('日期', fontsize=12)
    ax.set_ylabel('平均 GPU 使用率 (%)', fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    save_path = f'./plots/nodes_comparison_{start_date}_to_{end_date}.png'
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"節點對比圖已保存: {save_path}")
    plt.close()

def generate_gpu_usage_summary(start_date, end_date):
    """生成 GPU 使用率摘要圖"""
    nodes = ['colab-gpu1', 'colab-gpu2', 'colab-gpu3', 'colab-gpu4']
    gpu_ids = [1, 9, 17, 25, 33, 41, 49, 57]
    
    # 收集所有數據
    all_data = []
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    for node in nodes:
        for date in dates:
            date_str = date.strftime('%Y-%m-%d')
            avg_file = f"./data/{node}/{date_str}/average_{date_str}.csv"
            
            if os.path.exists(avg_file):
                try:
                    df = pd.read_csv(avg_file, encoding='utf-8')
                    if len(df.columns) >= 2:
                        df.columns = ['gpu', 'usage']
                        for _, row in df.iterrows():
                            if '全部平均' not in str(row['gpu']):
                                usage = pd.to_numeric(row['usage'], errors='coerce')
                                if not np.isnan(usage):
                                    all_data.append({
                                        'node': node,
                                        'date': date_str,
                                        'gpu': row['gpu'],
                                        'usage': usage
                                    })
                except:
                    continue
    
    if not all_data:
        print("未找到數據生成摘要圖")
        return
        
    df = pd.DataFrame(all_data)
    
    # 創建子圖
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 15))
    
    # 1. 各節點平均使用率
    node_avg = df.groupby('node')['usage'].mean()
    bars = ax1.bar(node_avg.index, node_avg.values, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
    ax1.set_title('各節點平均 GPU 使用率', fontsize=14, fontweight='bold')
    ax1.set_ylabel('平均使用率 (%)')
    for bar, value in zip(bars, node_avg.values):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{value:.2f}%', ha='center', va='bottom')
    
    # 2. 使用率分佈直方圖
    ax2.hist(df['usage'], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
    ax2.set_title('GPU 使用率分佈', fontsize=14, fontweight='bold')
    ax2.set_xlabel('使用率 (%)')
    ax2.set_ylabel('頻次')
    
    # 3. 每日趨勢
    daily_avg = df.groupby('date')['usage'].mean()
    ax3.plot(range(len(daily_avg)), daily_avg.values, marker='o', linewidth=2)
    ax3.set_title('每日平均 GPU 使用率趨勢', fontsize=14, fontweight='bold')
    ax3.set_xlabel('日期')
    ax3.set_ylabel('平均使用率 (%)')
    ax3.set_xticks(range(len(daily_avg)))
    ax3.set_xticklabels([d.split('-')[1] + '-' + d.split('-')[2] for d in daily_avg.index], rotation=45)
    
    # 4. 各 GPU 平均使用率
    gpu_avg = df.groupby('gpu')['usage'].mean().sort_values(ascending=False)
    ax4.bar(range(len(gpu_avg)), gpu_avg.values, color='lightcoral')
    ax4.set_title('各 GPU 平均使用率排名', fontsize=14, fontweight='bold')
    ax4.set_xlabel('GPU')
    ax4.set_ylabel('平均使用率 (%)')
    ax4.set_xticks(range(len(gpu_avg)))
    ax4.set_xticklabels(gpu_avg.index, rotation=45)
    
    plt.suptitle(f'GPU 使用率分析摘要 ({start_date} 至 {end_date})', 
                fontsize=18, fontweight='bold')
    plt.tight_layout()
    
    save_path = f'./plots/gpu_summary_{start_date}_to_{end_date}.png'
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"GPU 摘要圖已保存: {save_path}")
    plt.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python generate_plots.py START_DATE END_DATE")
        sys.exit(1)
    
    start_date = sys.argv[1]
    end_date = sys.argv[2]
    
    print(f"正在生成 {start_date} 至 {end_date} 的 GPU 使用率圖表...")
    
    try:
        generate_node_comparison(start_date, end_date)
        generate_gpu_usage_summary(start_date, end_date)
        print("所有圖表生成完成！")
    except Exception as e:
        print(f"生成圖表時發生錯誤: {e}")
        import traceback
        traceback.print_exc()
EOF

# 執行 Python 腳本生成圖表
echo "正在生成 GPU 使用率趨勢圖..."
$PYTHON_CMD generate_plots.py "$start_date" "$end_date"

# 清理臨時檔案
rm -f generate_plots.py

echo ""
echo "=== 執行完成 ==="
echo "圖表已保存到 ./plots/ 目錄"
echo "生成的圖表："
ls -la ./plots/*.png 2>/dev/null || echo "未找到生成的圖表檔案"

echo ""
echo "您也可以使用完整版工具："
echo "$PYTHON_CMD scripts/gpu_trend_visualizer.py --start-date $start_date --end-date $end_date --plot-type all"
