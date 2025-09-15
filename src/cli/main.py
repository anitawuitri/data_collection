"""AMD GPU 監控系統 CLI 主介面

使用 Click 框架提供現代化的命令列介面。
"""

import asyncio
import click
import logging
from datetime import datetime, date
from pathlib import Path
from typing import Optional

from ..infrastructure.config.settings import AppConfig
from .commands.collect import collect_command
from .commands.query import query_command
from .commands.visualize import visualize_command


# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
@click.option('--config-file', type=click.Path(exists=True), help='配置文件路徑')
@click.option('--data-dir', type=click.Path(), help='數據目錄路徑')
@click.option('--plots-dir', type=click.Path(), help='圖表輸出目錄路徑')
@click.option('--verbose', '-v', is_flag=True, help='詳細輸出模式')
@click.pass_context
def cli(ctx, config_file: Optional[str], data_dir: Optional[str], 
        plots_dir: Optional[str], verbose: bool):
    """🔥 AMD GPU 監控與視覺化系統 (重構版本)
    
    這是重構後的 AMD GPU 監控系統，提供模組化架構和現代化介面。
    
    主要功能：
    • 數據收集：從多節點收集 GPU 使用率和 VRAM 使用率
    • 使用者追蹤：整合管理 API 獲取使用者資訊  
    • 數據查詢：查詢特定使用者或時間範圍的 GPU 使用情況
    • 視覺化：生成各種統計圖表和趨勢分析
    """
    # 確保 context 物件存在
    ctx.ensure_object(dict)
    
    # 設定詳細輸出
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        click.echo("🔍 啟用詳細輸出模式")
    
    # 載入配置
    try:
        config = AppConfig.from_env()
        
        # 覆寫配置參數
        if data_dir:
            config.data_dir = Path(data_dir)
        if plots_dir:
            config.plots_dir = Path(plots_dir)
            
        ctx.obj['config'] = config
        
        if verbose:
            click.echo(f"📂 數據目錄: {config.data_dir}")
            click.echo(f"📊 圖表目錄: {config.plots_dir}")
            click.echo(f"🖥️  節點數量: {len(config.nodes)}")
            
    except Exception as e:
        click.echo(f"❌ 配置載入失敗: {e}", err=True)
        ctx.exit(1)


@cli.command()
@click.pass_context
def version(ctx):
    """顯示版本資訊"""
    click.echo("🔥 AMD GPU 監控系統 v3.0.0 (重構版本)")
    click.echo("採用模組化架構，提供更好的可維護性和擴展性")
    
    config = ctx.obj.get('config')
    if config:
        click.echo(f"數據目錄: {config.data_dir}")
        click.echo(f"圖表目錄: {config.plots_dir}")


@cli.command()
@click.pass_context  
def status(ctx):
    """檢查系統狀態"""
    config = ctx.obj.get('config')
    if not config:
        click.echo("❌ 配置未載入", err=True)
        return
    
    click.echo("🔍 系統狀態檢查")
    click.echo("=" * 50)
    
    # 檢查目錄
    if config.data_dir.exists():
        click.echo(f"✅ 數據目錄: {config.data_dir}")
    else:
        click.echo(f"⚠️  數據目錄不存在: {config.data_dir}")
    
    if config.plots_dir.exists():
        click.echo(f"✅ 圖表目錄: {config.plots_dir}")
    else:
        click.echo(f"⚠️  圖表目錄不存在: {config.plots_dir}")
        
    # 檢查節點配置
    click.echo(f"🖥️  配置節點數: {len(config.nodes)}")
    for node in config.nodes:
        click.echo(f"   • {node.name} ({node.ip}:{node.port})")
    
    # 檢查 GPU 配置
    click.echo(f"🎮 GPU 配置: {len(config.gpu.card_ids)} 個 GPU")
    click.echo(f"   Card IDs: {config.gpu.card_ids}")
    click.echo(f"   Indices: {config.gpu.indices}")


# 註冊子命令
cli.add_command(collect_command, name='collect')
cli.add_command(query_command, name='query') 
cli.add_command(visualize_command, name='visualize')


def main():
    """CLI 入口點"""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n⏹️  操作已取消", err=True)
    except Exception as e:
        click.echo(f"❌ 執行錯誤: {e}", err=True)
        raise


if __name__ == '__main__':
    main()