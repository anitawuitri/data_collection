"""數據查詢命令

提供數據查詢相關的 CLI 命令。
"""

import click
from datetime import datetime
from typing import Optional


@click.group()
def query_command():
    """🔍 數據查詢命令"""
    pass


@query_command.command('user')
@click.argument('username')
@click.argument('start_date', type=click.DateTime(formats=['%Y-%m-%d']))
@click.argument('end_date', type=click.DateTime(formats=['%Y-%m-%d']), required=False)
@click.option('--node', help='指定節點')
@click.option('--output', '-o', type=click.Choice(['table', 'json', 'csv']), 
              default='table', help='輸出格式')
@click.option('--plot', is_flag=True, help='生成使用趨勢圖')
@click.pass_context
def query_user(ctx, username: str, start_date: datetime, 
               end_date: Optional[datetime], node: Optional[str], 
               output: str, plot: bool):
    """查詢特定使用者的 GPU 使用情況
    
    查詢指定使用者在特定時間範圍內的 GPU 使用率和 VRAM 使用率。
    
    範例：
      gpu-monitor query user paslab_openai 2025-09-15
      gpu-monitor query user itrd 2025-09-10 2025-09-15
      gpu-monitor query user paslab_openai 2025-09-15 --plot
      gpu-monitor query user itrd 2025-09-15 --output json
    """
    config = ctx.obj.get('config')
    if not config:
        click.echo("❌ 配置未載入", err=True)
        return
    
    # 設定日期範圍
    start = start_date.date()
    end = end_date.date() if end_date else start
    
    if start > end:
        click.echo("❌ 開始日期不能晚於結束日期", err=True)
        return
    
    click.echo(f"🔍 查詢使用者 '{username}' 的 GPU 使用情況")
    click.echo(f"📅 日期範圍: {start} 至 {end}")
    
    if node:
        click.echo(f"🖥️  指定節點: {node}")
    
    # TODO: 實現使用者查詢邏輯
    click.echo("🚧 使用者查詢功能開發中...")
    
    if plot:
        click.echo("📊 生成使用趨勢圖...")


@query_command.command('users')
@click.argument('date', type=click.DateTime(formats=['%Y-%m-%d']))
@click.option('--node', help='指定節點')
@click.option('--active-only', is_flag=True, help='只顯示活躍使用者')
@click.option('--output', '-o', type=click.Choice(['table', 'json', 'csv']), 
              default='table', help='輸出格式')
@click.pass_context
def query_users(ctx, date: datetime, node: Optional[str], 
                active_only: bool, output: str):
    """列出指定日期的所有 GPU 使用者
    
    顯示指定日期內所有使用 GPU 的使用者及其使用情況。
    
    範例：
      gpu-monitor query users 2025-09-15
      gpu-monitor query users 2025-09-15 --node colab-gpu1
      gpu-monitor query users 2025-09-15 --active-only
    """
    config = ctx.obj.get('config')
    if not config:
        click.echo("❌ 配置未載入", err=True)
        return
    
    target_date = date.date()
    click.echo(f"📋 查詢 {target_date} 的所有 GPU 使用者")
    
    if node:
        click.echo(f"🖥️  指定節點: {node}")
    
    if active_only:
        click.echo("⚡ 只顯示活躍使用者 (GPU 使用率 > 1%)")
    
    # TODO: 實現使用者列表查詢邏輯
    click.echo("🚧 使用者列表查詢功能開發中...")


@query_command.command('stats')
@click.argument('start_date', type=click.DateTime(formats=['%Y-%m-%d']))
@click.argument('end_date', type=click.DateTime(formats=['%Y-%m-%d']), required=False)
@click.option('--node', help='指定節點')
@click.option('--gpu', type=int, help='指定 GPU 索引')
@click.option('--detailed', is_flag=True, help='詳細統計資訊')
@click.pass_context
def query_stats(ctx, start_date: datetime, end_date: Optional[datetime], 
                node: Optional[str], gpu: Optional[int], detailed: bool):
    """查詢 GPU 使用統計
    
    顯示 GPU 使用率、VRAM 使用率的統計資訊。
    
    範例：
      gpu-monitor query stats 2025-09-15
      gpu-monitor query stats 2025-09-10 2025-09-15
      gpu-monitor query stats 2025-09-15 --node colab-gpu1 --gpu 0
      gpu-monitor query stats 2025-09-15 --detailed
    """
    config = ctx.obj.get('config')
    if not config:
        click.echo("❌ 配置未載入", err=True)
        return
    
    # 設定日期範圍
    start = start_date.date()
    end = end_date.date() if end_date else start
    
    click.echo(f"📊 查詢 GPU 使用統計")
    click.echo(f"📅 日期範圍: {start} 至 {end}")
    
    if node:
        click.echo(f"🖥️  指定節點: {node}")
    
    if gpu is not None:
        click.echo(f"🎮 指定 GPU: GPU[{gpu}]")
    
    if detailed:
        click.echo("📋 詳細統計模式")
    
    # TODO: 實現統計查詢邏輯
    click.echo("🚧 統計查詢功能開發中...")


@query_command.command('search')
@click.argument('pattern')
@click.option('--start-date', type=click.DateTime(formats=['%Y-%m-%d']), 
              help='搜尋開始日期')
@click.option('--end-date', type=click.DateTime(formats=['%Y-%m-%d']), 
              help='搜尋結束日期')
@click.option('--field', type=click.Choice(['user', 'node', 'all']), 
              default='all', help='搜尋欄位')
@click.pass_context
def query_search(ctx, pattern: str, start_date: Optional[datetime], 
                 end_date: Optional[datetime], field: str):
    """搜尋 GPU 使用記錄
    
    在數據中搜尋符合條件的使用記錄。
    
    範例：
      gpu-monitor query search paslab
      gpu-monitor query search gpu1 --field node
      gpu-monitor query search paslab_openai --start-date 2025-09-01
    """
    config = ctx.obj.get('config')
    if not config:
        click.echo("❌ 配置未載入", err=True)
        return
    
    click.echo(f"🔎 搜尋模式: '{pattern}'")
    click.echo(f"🎯 搜尋欄位: {field}")
    
    if start_date:
        start = start_date.date()
        end = end_date.date() if end_date else start
        click.echo(f"📅 搜尋範圍: {start} 至 {end}")
    
    # TODO: 實現搜尋邏輯
    click.echo("🚧 搜尋功能開發中...")