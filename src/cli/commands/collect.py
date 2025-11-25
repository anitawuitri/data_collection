"""數據收集命令

提供數據收集相關的 CLI 命令。
"""

import asyncio
import click
from datetime import datetime, date, timedelta
from typing import Optional

from ...tools.daily_collector import DailyGPUCollector


@click.group()
def collect_command():
    """🔄 數據收集命令"""
    pass


@collect_command.command('daily')
@click.option('--date', type=click.DateTime(formats=['%Y-%m-%d']), 
              help='指定日期 (YYYY-MM-DD)，默認為今天')
@click.option('--nodes', multiple=True, help='指定節點，可多選')
@click.option('--data-dir', default='./data', help='數據輸出目錄')
@click.option('--dry-run', is_flag=True, help='試運行模式，不實際收集數據')
@click.pass_context
def collect_daily(ctx, date: Optional[datetime], nodes: tuple, 
                  data_dir: str, dry_run: bool):
    """收集每日 GPU 數據
    
    從所有節點收集 GPU 使用率、VRAM 使用率和使用者資訊。
    
    範例：
      python -m src collect daily --date 2025-09-15
      python -m src collect daily --nodes colab-gpu1 --nodes colab-gpu2
      python -m src collect daily --dry-run
    """
    # 設定日期
    target_date = date.date() if date else datetime.now().date()
    click.echo(f"📅 收集日期: {target_date}")
    
    # 設定目標節點
    target_nodes = list(nodes) if nodes else None
    if target_nodes:
        click.echo(f"🖥️  目標節點: {', '.join(target_nodes)}")
    
    click.echo(f"📄 輸出格式: csv")
    
    if dry_run:
        click.echo("🧪 試運行模式：不會實際收集數據")
        return
    
    try:
        click.echo("🚀 開始數據收集...")
        
        # 使用簡化的收集器
        collector = DailyGPUCollector(data_dir=data_dir)
        success = asyncio.run(collector.collect_daily_data(target_date, target_nodes))
        
        if success:
            click.echo("✅ 收集完成!")
        else:
            click.echo("❌ 收集失敗", err=True)
        
    except Exception as e:
        click.echo(f"❌ 數據收集失敗: {e}", err=True)
        if ctx.obj.get('verbose'):
            import traceback
            click.echo(traceback.format_exc(), err=True)


@collect_command.command('test')
@click.option('--node', help='測試指定節點')
@click.pass_context
def collect_test(ctx, node: Optional[str]):
    """測試數據收集連線
    
    測試與 Netdata API 和管理 API 的連線狀態。
    """
    click.echo("🔍 測試數據收集連線...")
    
    # 簡化的測試
    collector = DailyGPUCollector()
    
    try:
        # 測試配置載入
        if collector.config.nodes:
            click.echo(f"✅ 配置載入成功，找到 {len(collector.config.nodes)} 個節點")
            
            for test_node in collector.config.nodes:
                if not node or test_node.name == node:
                    click.echo(f"  • {test_node.name} ({test_node.netdata_url}): 🟢 配置正常")
        
        # 測試管理 API 配置
        if collector.config.api.bearer_token:
            click.echo(f"✅ 管理 API 配置正常")
        else:
            click.echo(f"⚠️  管理 API 未配置 Bearer Token")
        
        click.echo("\n✅ 配置檢查通過！")
        
    except Exception as e:
        click.echo(f"❌ 測試失敗: {e}", err=True)