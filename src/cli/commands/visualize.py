"""視覺化命令

提供 GPU 數據視覺化相關的 CLI 命令。
簡化版本，去掉不必要的複雜功能。
"""

import click
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Optional

from ...visualization.main import SimpleVisualizer


@click.group()
def visualize_command():
    """📊 數據視覺化命令"""
    pass


@visualize_command.command('daily')
@click.argument('date', type=click.DateTime(formats=['%Y-%m-%d']))
@click.option('--nodes', help='指定節點，逗號分隔')
@click.option('--data-dir', default='./data', help='數據目錄')
@click.option('--output-dir', default='./plots', help='輸出目錄')
@click.pass_context
def visualize_daily(ctx, date: datetime, nodes: str, data_dir: str, output_dir: str):
    """生成每日 GPU 視覺化圖表
    
    從收集的數據生成各種視覺化圖表。
    
    範例：
      python -m src visualize daily 2025-09-19
      python -m src visualize daily 2025-09-19 --nodes colab-gpu1,colab-gpu2
    """
    date_str = date.date().isoformat()
    
    # 解析節點
    target_nodes = None
    if nodes:
        target_nodes = [n.strip() for n in nodes.split(',')]
    
    click.echo(f"� 生成 {date_str} 的視覺化圖表")
    if target_nodes:
        click.echo(f"🖥️  目標節點: {', '.join(target_nodes)}")
    
    try:
        visualizer = SimpleVisualizer(data_dir, output_dir)
        files = visualizer.generate_daily_plots(date_str, target_nodes)
        
        click.echo(f"✅ 生成完成! 共 {len(files)} 個圖表文件:")
        for file_path in files:
            click.echo(f"   📈 {Path(file_path).name}")
            
    except Exception as e:
        click.echo(f"❌ 視覺化失敗: {e}", err=True)
        if ctx.obj and ctx.obj.get('verbose'):
            import traceback
            click.echo(traceback.format_exc(), err=True)


@visualize_command.command('test-fonts')
@click.option('--output-dir', default='./plots', help='輸出目錄')
def visualize_test_fonts(output_dir: str):
    """測試中文字體配置
    
    生成測試圖表以驗證中文字體是否正確顯示。
    """
    click.echo("🔤 測試中文字體配置...")
    
    try:
        visualizer = SimpleVisualizer(output_dir=output_dir)
        file_path = visualizer.test_fonts()
        
        click.echo(f"✅ 字體測試完成:")
        click.echo(f"   � {Path(file_path).name}")
        
    except Exception as e:
        click.echo(f"❌ 字體測試失敗: {e}", err=True)


@visualize_command.command('auto')
@click.option('--data-dir', default='./data', help='數據目錄')
@click.option('--output-dir', default='./plots', help='輸出目錄')
@click.option('--days', default=7, help='生成最近幾天的圖表')
def visualize_auto(data_dir: str, output_dir: str, days: int):
    """自動生成最近幾天的視覺化圖表
    
    自動掃描數據目錄並生成可用日期的圖表。
    """
    click.echo(f"🔍 自動掃描最近 {days} 天的數據...")
    
    data_path = Path(data_dir)
    if not data_path.exists():
        click.echo(f"❌ 數據目錄不存在: {data_dir}", err=True)
        return
    
    visualizer = SimpleVisualizer(data_dir, output_dir)
    generated_count = 0
    
    # 檢查最近幾天的數據
    for i in range(days):
        target_date = date.today() - timedelta(days=i)
        date_str = target_date.isoformat()
        
        # 檢查是否有該日期的數據
        available_nodes = visualizer._discover_nodes(date_str)
        
        if available_nodes:
            click.echo(f"📅 處理 {date_str} ({len(available_nodes)} 個節點)")
            try:
                files = visualizer.generate_daily_plots(date_str, available_nodes)
                generated_count += len(files)
                click.echo(f"   ✅ 生成 {len(files)} 個圖表")
            except Exception as e:
                click.echo(f"   ⚠️  生成失敗: {e}")
    
    click.echo(f"\n� 自動生成完成! 總共生成 {generated_count} 個圖表文件")