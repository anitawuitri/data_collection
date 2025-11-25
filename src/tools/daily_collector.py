"""簡化的日常 GPU 數據收集工具

替代原來的 python/daily_gpu_log.py，使用現有的模塊化架構。
不搞那些企業級的垃圾，直接幹活！
"""

import asyncio
import logging
import sys
from datetime import datetime, date
from pathlib import Path
from typing import Optional, List

# 動態導入以避免依賴問題
try:
    from ..infrastructure.config.settings import AppConfig
    from ..core.collectors.netdata_collector import NetdataCollector
    from ..core.collectors.management_collector import ManagementCollector
    from ..core.services.daily_export_service import DailyExportService
    HAS_DEPENDENCIES = True
except ImportError as e:
    print(f"⚠️  模組導入失敗: {e}")
    print("💡 回退到簡化模式...")
    HAS_DEPENDENCIES = False

logger = logging.getLogger(__name__)


class DailyGPUCollector:
    """日常 GPU 數據收集器
    
    簡化版本，去掉不必要的複雜性。
    """
    
    def __init__(self, data_dir: str = "./data"):
        if not HAS_DEPENDENCIES:
            print("❌ 缺少必要的依賴，無法繼續")
            sys.exit(1)
            
        self.config = AppConfig.from_env()
        self.netdata_collector = NetdataCollector(self.config)
        self.management_collector = ManagementCollector(self.config)
        self.export_service = DailyExportService(Path(data_dir))
    
    async def collect_daily_data(self, target_date: date, nodes: Optional[List[str]] = None) -> bool:
        """收集日常數據
        
        簡化的收集流程，直接輸出結果。
        
        Args:
            target_date: 目標日期
            nodes: 指定節點 (None = 所有節點)
            
        Returns:
            收集是否成功
        """
        date_str = target_date.isoformat()
        target_nodes = nodes or [node.name for node in self.config.nodes]
        
        logger.info(f"開始收集 {date_str} 的數據，目標節點: {target_nodes}")
        
        # 嘗試收集使用者資訊 (可選)
        user_tasks = {}
        if self.config.api.bearer_token:
            try:
                logger.info("收集使用者任務資訊...")
                user_task_data = await self.management_collector.collect_user_tasks(target_date)
                user_tasks = user_task_data.get('gpu_user_mapping', {})
                logger.info(f"收集到 {len(user_task_data.get('users', []))} 個使用者任務")
            except Exception as e:
                logger.warning(f"無法收集使用者資訊: {e}")
        
        success_count = 0
        
        # 收集各節點數據
        for node_name in target_nodes:
            node_config = self.config.get_node_by_name(node_name)
            if not node_config:
                logger.error(f"找不到節點配置: {node_name}")
                continue
            
            try:
                logger.info(f"收集 {node_name} 數據...")
                
                # 收集 GPU 數據
                gpu_data = await self.netdata_collector.collect_daily_gpu_data(node_config, target_date)
                
                # 映射使用者到 GPU
                gpu_user_mapping = self._map_users_to_gpus(user_tasks, node_name)
                
                # 導出數據
                files = self.export_service.export_node_data(
                    node_name, date_str, gpu_data, gpu_user_mapping
                )
                
                logger.info(f"{node_name} 收集完成，生成 {len(files)} 個文件")
                success_count += 1
                
            except Exception as e:
                logger.error(f"收集 {node_name} 失敗: {e}")
                continue
        
        logger.info(f"數據收集完成: {success_count}/{len(target_nodes)} 節點成功")
        return success_count > 0
    
    def _map_users_to_gpus(self, user_tasks: dict, node_name: str) -> dict:
        """將使用者映射到 GPU
        
        簡化的映射邏輯，不搞複雜的絕對 ID 轉換。
        """
        if not user_tasks:
            return {}
        
        gpu_mapping = {}
        
        # 簡單策略：根據節點名稱和 GPU 數量分配
        node_users = []
        for user_info in user_tasks.values():
            if node_name.lower() in user_info.get('hostname', '').lower():
                node_users.append(user_info)
        
        # 按 GPU 數量分配用戶到 GPU 卡
        card_index = 0
        for user_info in node_users:
            gpu_count = user_info.get('gpu_count', 1)
            username = user_info.get('username', 'unknown')
            
            # 分配連續的 GPU 卡給這個用戶
            for _ in range(gpu_count):
                if card_index < len(self.config.gpu.card_ids):
                    card_id = self.config.gpu.card_ids[card_index]
                    gpu_mapping[card_id] = username
                    card_index += 1
        
        return gpu_mapping


def main():
    """主程式入口"""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(
        description='日常 GPU 數據收集工具 (重構版)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例用法:
  python -m src.tools.daily_collector                    # 收集今天的數據
  python -m src.tools.daily_collector 2025-09-19        # 收集指定日期
  python -m src.tools.daily_collector --nodes gpu1,gpu2  # 指定節點
        """
    )
    
    parser.add_argument(
        'date',
        nargs='?',
        help='指定日期 (YYYY-MM-DD)，默認今天'
    )
    
    parser.add_argument(
        '--nodes',
        help='指定節點，逗號分隔 (如: colab-gpu1,colab-gpu2)'
    )
    
    parser.add_argument(
        '--data-dir',
        default='./data',
        help='數據輸出目錄 (默認: ./data)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='詳細輸出'
    )
    
    args = parser.parse_args()
    
    # 設置日誌
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # 解析日期
    if args.date:
        try:
            target_date = datetime.strptime(args.date, '%Y-%m-%d').date()
        except ValueError:
            print(f"錯誤: 日期格式無效 '{args.date}'，請使用 YYYY-MM-DD")
            sys.exit(1)
    else:
        target_date = datetime.now().date()
    
    # 解析節點
    nodes = None
    if args.nodes:
        nodes = [n.strip() for n in args.nodes.split(',')]
    
    # 運行收集器
    try:
        collector = DailyGPUCollector(data_dir=args.data_dir)
        success = asyncio.run(collector.collect_daily_data(target_date, nodes))
        
        if success:
            print("✅ 數據收集完成")
            sys.exit(0)
        else:
            print("❌ 數據收集失敗")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  用戶中斷操作")
        sys.exit(130)
    except Exception as e:
        print(f"💥 錯誤: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()