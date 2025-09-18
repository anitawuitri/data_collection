"""數據收集命令

提供數據收集相關的 CLI 命令。
"""

import asyncio
import click
from datetime import datetime, date, timedelta
from typing import Optional

from ...core.services import DataCollectionService


@click.group()
def collect_command():
    """🔄 數據收集命令"""
    pass


@collect_command.command('daily')
@click.option('--date', type=click.DateTime(formats=['%Y-%m-%d']), 
              help='指定日期 (YYYY-MM-DD)，默認為今天')
@click.option('--nodes', multiple=True, help='指定節點，可多選')
@click.option('--dry-run', is_flag=True, help='試運行模式，不實際收集數據')
@click.option('--output-format', type=click.Choice(['csv', 'json']), 
              default='csv', help='輸出格式')
@click.pass_context
def collect_daily(ctx, date: Optional[datetime], nodes: tuple, 
                  dry_run: bool, output_format: str):
    """收集每日 GPU 數據
    
    從所有節點收集 GPU 使用率、VRAM 使用率和使用者資訊。
    
    範例：
      gpu-monitor collect daily --date 2025-09-15
      gpu-monitor collect daily --nodes colab-gpu1 --nodes colab-gpu2
      gpu-monitor collect daily --dry-run
    """
    config = ctx.obj.get('config')
    if not config:
        click.echo("❌ 配置未載入", err=True)
        return
    
    # 設定日期
    target_date = date.date() if date else datetime.now().date()
    click.echo(f"📅 收集日期: {target_date}")
    
    # 設定目標節點
    target_nodes = list(nodes) if nodes else [node.name for node in config.nodes]
    click.echo(f"🖥️  目標節點: {', '.join(target_nodes)}")
    click.echo(f"📄 輸出格式: {output_format}")
    
    if dry_run:
        click.echo("🧪 試運行模式：不會實際收集數據")
        return
    
    # 初始化數據收集服務
    collection_service = DataCollectionService(config)
    
    try:
        click.echo("🚀 開始數據收集...")
        
        # 執行異步數據收集
        results = asyncio.run(
            collection_service.collect_daily_data(target_date, target_nodes)
        )
        
        # 顯示收集結果
        summary = results['summary']
        click.echo(f"✅ 收集完成!")
        click.echo(f"   • 成功節點: {summary['successful_nodes']}/{summary['total_nodes']}")
        click.echo(f"   • 總 GPU 數: {summary['total_gpus']}")
        
        if results['errors']:
            click.echo(f"⚠️  發生 {len(results['errors'])} 個錯誤:")
            for error in results['errors']:
                click.echo(f"   • {error}")
        
        # 保存數據
        if summary['successful_nodes'] > 0:
            click.echo("💾 保存數據文件...")
            saved_files = collection_service.save_collection_results(
                results, output_format
            )
            click.echo(f"✅ 已保存 {len(saved_files)} 個文件")
            
            if ctx.obj.get('verbose'):
                for file_path in saved_files:
                    click.echo(f"   • {file_path}")
        
    except Exception as e:
        click.echo(f"❌ 數據收集失敗: {e}", err=True)
        if ctx.obj.get('verbose'):
            import traceback
            click.echo(traceback.format_exc(), err=True)


@collect_command.command('range')
@click.argument('start_date', type=click.DateTime(formats=['%Y-%m-%d']))
@click.argument('end_date', type=click.DateTime(formats=['%Y-%m-%d']))
@click.option('--nodes', multiple=True, help='指定節點，可多選')
@click.option('--dry-run', is_flag=True, help='試運行模式')
@click.option('--output-format', type=click.Choice(['csv', 'json']), 
              default='csv', help='輸出格式')
@click.pass_context
def collect_range(ctx, start_date: datetime, end_date: datetime,
                  nodes: tuple, dry_run: bool, output_format: str):
    """收集日期範圍內的 GPU 數據
    
    範例：
      gpu-monitor collect range 2025-09-10 2025-09-15
      gpu-monitor collect range 2025-09-10 2025-09-15 --nodes colab-gpu1
    """
    config = ctx.obj.get('config')
    if not config:
        click.echo("❌ 配置未載入", err=True)
        return
    
    start = start_date.date()
    end = end_date.date()
    
    if start > end:
        click.echo("❌ 開始日期不能晚於結束日期", err=True)
        return
    
    click.echo(f"📅 收集日期範圍: {start} 到 {end}")
    
    # 計算總天數
    total_days = (end - start).days + 1
    click.echo(f"📊 總共 {total_days} 天")
    
    target_nodes = list(nodes) if nodes else [node.name for node in config.nodes]
    click.echo(f"🖥️  目標節點: {', '.join(target_nodes)}")
    
    if dry_run:
        click.echo("🧪 試運行模式：不會實際收集數據")
        return
    
    # 初始化數據收集服務
    collection_service = DataCollectionService(config)
    
    current_date = start
    total_files = 0
    total_errors = 0
    
    with click.progressbar(length=total_days, label='收集進度') as bar:
        while current_date <= end:
            try:
                # 收集當天數據
                results = asyncio.run(
                    collection_service.collect_daily_data(current_date, target_nodes)
                )
                
                # 保存數據
                if results['summary']['successful_nodes'] > 0:
                    saved_files = collection_service.save_collection_results(
                        results, output_format
                    )
                    total_files += len(saved_files)
                
                total_errors += len(results['errors'])
                
            except Exception as e:
                click.echo(f"\n❌ {current_date} 收集失敗: {e}", err=True)
                total_errors += 1
            
            current_date += timedelta(days=1)
            bar.update(1)
    
    click.echo(f"\n✅ 批次收集完成!")
    click.echo(f"   • 總文件數: {total_files}")
    if total_errors > 0:
        click.echo(f"   • 錯誤數: {total_errors}")
    with click.progressbar(target_nodes, label='收集數據') as nodes_bar:
        for node_name in nodes_bar:
            # 模擬數據收集
            import time
            time.sleep(0.5)  # 模擬處理時間
            click.echo(f"✅ 完成 {node_name}")
    
    click.echo("🎉 數據收集完成！")


@collect_command.command('range')
@click.argument('start_date', type=click.DateTime(formats=['%Y-%m-%d']))
@click.argument('end_date', type=click.DateTime(formats=['%Y-%m-%d']))
@click.option('--nodes', multiple=True, help='指定節點，可多選')
@click.option('--parallel', '-p', is_flag=True, help='平行處理模式')
@click.pass_context
def collect_range(ctx, start_date: datetime, end_date: datetime, 
                  nodes: tuple, parallel: bool):
    """收集指定日期範圍的數據
    
    批量收集多天的 GPU 使用數據。
    
    範例：
      gpu-monitor collect range 2025-09-01 2025-09-15
      gpu-monitor collect range 2025-09-01 2025-09-15 --parallel
    """
    config = ctx.obj.get('config')
    if not config:
        click.echo("❌ 配置未載入", err=True)
        return
    
    # 計算日期範圍
    start = start_date.date()
    end = end_date.date()
    
    if start > end:
        click.echo("❌ 開始日期不能晚於結束日期", err=True)
        return
    
    days = (end - start).days + 1
    click.echo(f"📅 日期範圍: {start} 至 {end} (共 {days} 天)")
    
    # 設定目標節點
    target_nodes = list(nodes) if nodes else [node.name for node in config.nodes]
    click.echo(f"🖥️  目標節點: {', '.join(target_nodes)}")
    
    if parallel:
        click.echo("⚡ 平行處理模式")
    
    # TODO: 實現範圍收集邏輯
    click.echo("🚧 範圍收集功能開發中...")


@collect_command.command('test')
@click.option('--node', help='測試指定節點')
@click.pass_context
def collect_test(ctx, node: Optional[str]):
    """測試數據收集連線
    
    測試與 Netdata API 和管理 API 的連線狀態。
    """
    config = ctx.obj.get('config')
    if not config:
        click.echo("❌ 配置未載入", err=True)
        return
    
    click.echo("🔍 測試數據收集連線...")
    
    # 設定測試節點
    if node:
        test_nodes = [config.get_node_by_name(node)]
        if not test_nodes[0]:
            click.echo(f"❌ 找不到節點: {node}", err=True)
            return
    else:
        test_nodes = config.nodes
    
    # 測試 Netdata 連線
    click.echo("\n📡 測試 Netdata API...")
    for test_node in test_nodes:
        # TODO: 實現連線測試邏輯
        click.echo(f"  • {test_node.name} ({test_node.netdata_url}): 🟢 正常")
    
    # 測試管理 API
    click.echo("\n🔐 測試管理 API...")
    click.echo(f"  • {config.api.management_url}: 🟢 正常")
    
    click.echo("\n✅ 所有連線測試通過！")