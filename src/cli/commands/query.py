"""數據查詢命令

提供數據查詢相關的 CLI 命令。
"""

import click
import json
from datetime import datetime, date, timedelta
from typing import Optional

from ...core.services import DataProcessingService


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
    
    click.echo(f"🔍 查詢使用者: {username}")
    click.echo(f"📅 日期範圍: {start} 到 {end}")
    
    # 初始化數據處理服務
    processing_service = DataProcessingService(config)
    
    # 確定目標節點
    target_nodes = [node] if node else [n.name for n in config.nodes]
    
    # 載入數據並搜尋使用者
    user_data = []
    
    try:
        # 載入多節點數據
        multi_node_data = processing_service.load_multi_node_data(
            target_nodes, start, end
        )
        
        # 搜尋使用者數據
        for node_name, node_dates in multi_node_data.items():
            for date_str, node_data in node_dates.items():
                if node_data.get('averages'):
                    for gpu_name, avg_data in node_data['averages'].items():
                        if avg_data['user'].lower() == username.lower():
                            user_data.append({
                                'date': date_str,
                                'node': node_name,
                                'gpu': gpu_name,
                                'usage': avg_data['usage'],
                                'vram': avg_data['vram']
                            })
        
        if not user_data:
            click.echo(f"❌ 未找到使用者 '{username}' 的使用記錄")
            return
        
        # 輸出結果
        if output == 'table':
            _print_user_table(user_data)
        elif output == 'json':
            click.echo(json.dumps(user_data, indent=2, ensure_ascii=False))
        elif output == 'csv':
            _print_user_csv(user_data)
        
        # 生成統計摘要
        total_usage = sum(record['usage'] for record in user_data)
        total_vram = sum(record['vram'] for record in user_data)
        avg_usage = total_usage / len(user_data)
        avg_vram = total_vram / len(user_data)
        
        click.echo(f"\n📊 統計摘要:")
        click.echo(f"   • 總記錄數: {len(user_data)}")
        click.echo(f"   • 平均 GPU 使用率: {avg_usage:.1f}%")
        click.echo(f"   • 平均 VRAM 使用率: {avg_vram:.1f}%")
        click.echo(f"   • 使用的節點: {len(set(r['node'] for r in user_data))}")
        
    except Exception as e:
        click.echo(f"❌ 查詢失敗: {e}", err=True)


@query_command.command('stats')
@click.argument('start_date', type=click.DateTime(formats=['%Y-%m-%d']))
@click.argument('end_date', type=click.DateTime(formats=['%Y-%m-%d']))
@click.option('--nodes', multiple=True, help='指定節點，可多選')
@click.option('--output', '-o', type=click.Choice(['table', 'json']), 
              default='table', help='輸出格式')
@click.option('--detailed', is_flag=True, help='顯示詳細統計')
@click.pass_context
def query_stats(ctx, start_date: datetime, end_date: datetime,
                nodes: tuple, output: str, detailed: bool):
    """查詢系統使用統計
    
    生成指定日期範圍內的系統使用率統計報告。
    
    範例：
      gpu-monitor query stats 2025-09-10 2025-09-15
      gpu-monitor query stats 2025-09-10 2025-09-15 --detailed
      gpu-monitor query stats 2025-09-10 2025-09-15 --nodes colab-gpu1 --output json
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
    
    # 確定目標節點
    target_nodes = list(nodes) if nodes else [n.name for n in config.nodes]
    
    click.echo(f"📊 系統統計查詢")
    click.echo(f"📅 日期範圍: {start} 到 {end}")
    click.echo(f"🖥️  目標節點: {', '.join(target_nodes)}")
    
    # 初始化數據處理服務
    processing_service = DataProcessingService(config)
    
    try:
        # 載入多節點數據
        multi_node_data = processing_service.load_multi_node_data(
            target_nodes, start, end
        )
        
        if not multi_node_data:
            click.echo("❌ 未找到可用數據")
            return
        
        # 生成使用率報告
        if detailed:
            report = processing_service.generate_usage_report(multi_node_data)
            
            if output == 'json':
                click.echo(json.dumps(report, indent=2, ensure_ascii=False))
            else:
                _print_detailed_report(report)
        else:
            # 簡單摘要
            summary = processing_service.calculate_multi_node_summary(multi_node_data)
            
            if output == 'json':
                click.echo(json.dumps(summary, indent=2, ensure_ascii=False))
            else:
                _print_summary_table(summary)
    
    except Exception as e:
        click.echo(f"❌ 統計查詢失敗: {e}", err=True)


def _print_user_table(user_data):
    """以表格格式列印使用者數據"""
    click.echo("\n📋 使用者 GPU 使用記錄:")
    click.echo("-" * 70)
    click.echo(f"{'日期':<12} {'節點':<12} {'GPU':<8} {'使用率':<8} {'VRAM':<8}")
    click.echo("-" * 70)
    
    for record in sorted(user_data, key=lambda x: (x['date'], x['node'], x['gpu'])):
        click.echo(f"{record['date']:<12} {record['node']:<12} "
                  f"{record['gpu']:<8} {record['usage']:>6.1f}% {record['vram']:>6.1f}%")


def _print_user_csv(user_data):
    """以 CSV 格式列印使用者數據"""
    click.echo("日期,節點,GPU,使用率(%),VRAM(%)")
    for record in sorted(user_data, key=lambda x: (x['date'], x['node'], x['gpu'])):
        click.echo(f"{record['date']},{record['node']},{record['gpu']},"
                  f"{record['usage']:.1f},{record['vram']:.1f}")


def _print_summary_table(summary):
    """列印摘要統計表格"""
    click.echo(f"\n📊 系統使用摘要 ({summary['date_range']['start']} 到 {summary['date_range']['end']}):")
    click.echo("-" * 80)
    
    overall = summary['overall_stats']
    click.echo(f"整體統計:")
    click.echo(f"  • 總節點數: {summary['total_nodes']}")
    click.echo(f"  • 總天數: {summary['date_range']['total_days']}")
    click.echo(f"  • 活躍 GPU: {overall['active_gpus']}")
    click.echo(f"  • 平均使用率: {overall['avg_utilization']:.1f}%")
    click.echo(f"  • 平均 VRAM: {overall['avg_vram']:.1f}%")
    
    click.echo(f"\n📈 各節點統計:")
    for node_name, node_summary in summary['node_summaries'].items():
        click.echo(f"  {node_name}:")
        click.echo(f"    - 數據天數: {node_summary['total_days']}")
        click.echo(f"    - 平均使用率: {node_summary['avg_utilization']:.1f}%")
        click.echo(f"    - 平均 VRAM: {node_summary['avg_vram']:.1f}%")


def _print_detailed_report(report):
    """列印詳細報告"""
    summary = report['summary']
    
    # 列印基本摘要
    _print_summary_table(summary)
    
    # 列印建議
    if report['recommendations']:
        click.echo(f"\n💡 使用建議:")
        for recommendation in report['recommendations']:
            click.echo(f"  {recommendation}")
    
    # 列印高使用率時段
    click.echo(f"\n🔥 高使用率時段 (>80%):")
    all_peaks = []
    for node_name, node_details in report['node_details'].items():
        for peak in node_details['peak_periods']:
            peak['node'] = node_name
            all_peaks.append(peak)
    
    # 按持續時間排序，取前5個
    all_peaks.sort(key=lambda x: x['duration_minutes'], reverse=True)
    for peak in all_peaks[:5]:
        start_time = datetime.fromtimestamp(peak['start_time'])
        click.echo(f"  {peak['node']} {peak['gpu']}: "
                  f"{start_time.strftime('%Y-%m-%d %H:%M')} "
                  f"({peak['duration_minutes']:.0f}分鐘, "
                  f"最高 {peak['max_usage']:.1f}%)")
    
    if not all_peaks:
        click.echo("  無高使用率時段")
    
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