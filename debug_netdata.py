#!/usr/bin/env python3
"""Netdata API 測試腳本

測試 Netdata API 連接和回應格式
"""

import asyncio
import aiohttp
import json
from datetime import datetime, date, timedelta
from urllib.parse import urlencode


async def test_netdata_api():
    """測試 Netdata API"""
    
    # 測試配置
    nodes = [
        ("colab-gpu1", "192.168.10.103", 19999),
        ("colab-gpu2", "192.168.10.104", 19999),
        ("colab-gpu3", "192.168.10.105", 19999),
        ("colab-gpu4", "192.168.10.106", 19999),
    ]
    
    # GPU Card IDs
    card_ids = [1, 9, 17, 25, 33, 41, 49, 57]
    
    # 時間範圍 (今天)
    target_date = date.today()
    start_time = datetime.combine(target_date, datetime.min.time())
    end_time = start_time + timedelta(days=1, seconds=-1)
    
    timestamp_start = int(start_time.timestamp())
    timestamp_end = int(end_time.timestamp())
    
    print(f"🔍 測試 Netdata API 連接")
    print(f"時間範圍: {start_time} 到 {end_time}")
    print("=" * 60)
    
    timeout = aiohttp.ClientTimeout(total=10)
    
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for node_name, ip, port in nodes:
            print(f"\n📊 測試節點: {node_name} ({ip}:{port})")
            
            # 測試節點可達性
            netdata_url = f"http://{ip}:{port}"
            
            try:
                # 首先測試 info API
                info_url = f"{netdata_url}/api/v1/info"
                async with session.get(info_url) as response:
                    if response.status == 200:
                        print(f"✅ 節點 {node_name} 可達")
                        info_data = await response.json()
                        print(f"   Netdata 版本: {info_data.get('version', 'unknown')}")
                    else:
                        print(f"❌ 節點 {node_name} 不可達: HTTP {response.status}")
                        continue
                        
            except Exception as e:
                print(f"❌ 節點 {node_name} 連接失敗: {e}")
                continue
            
            # 測試第一個 GPU 的數據
            test_card_id = card_ids[0]  # 測試 card1
            print(f"   測試 GPU Card {test_card_id}...")
            
            # 測試 GPU 使用率 API
            gpu_chart = f"amdgpu.gpu_utilization_unknown_AMD_GPU_card{test_card_id}"
            params = {
                'chart': gpu_chart,
                'format': 'json',
                'points': 10,  # 只取 10 個點進行測試
                'after': timestamp_start,
                'before': timestamp_end
            }
            
            data_url = f"{netdata_url}/api/v1/data?" + urlencode(params)
            print(f"   請求 URL: {data_url}")
            
            try:
                async with session.get(data_url) as response:
                    if response.status == 200:
                        try:
                            data = await response.json()
                            print(f"   ✅ GPU 使用率 API 回應成功")
                            print(f"   回應欄位: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                            
                            if isinstance(data, dict):
                                # 顯示數據結構
                                if 'data' in data:
                                    data_points = data['data']
                                    print(f"   數據點數: {len(data_points)}")
                                    if len(data_points) > 0:
                                        print(f"   第一個數據點: {data_points[0]}")
                                        print(f"   最後數據點: {data_points[-1]}")
                                    else:
                                        print(f"   ⚠️ 無數據點")
                                
                                if 'labels' in data:
                                    print(f"   標籤: {data['labels']}")
                                
                                if 'latest_values' in data:
                                    print(f"   最新值: {data['latest_values']}")
                                
                                # 檢查其他可能的欄位
                                other_fields = [k for k in data.keys() if k not in ['data', 'labels', 'latest_values']]
                                if other_fields:
                                    print(f"   其他欄位: {other_fields}")
                            
                        except json.JSONDecodeError as e:
                            response_text = await response.text()
                            print(f"   ❌ JSON 解析失敗: {e}")
                            print(f"   回應內容: {response_text[:200]}...")
                    
                    else:
                        response_text = await response.text()
                        print(f"   ❌ API 請求失敗: HTTP {response.status}")
                        print(f"   回應內容: {response_text[:200]}...")
                        
            except Exception as e:
                print(f"   ❌ API 請求異常: {e}")
            
            print("-" * 40)


if __name__ == '__main__':
    print("🧪 Netdata API 連接測試")
    asyncio.run(test_netdata_api())
    print("\n✅ 測試完成")