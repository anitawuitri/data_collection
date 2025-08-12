# #!/bin/bash
# NETDATA_HOST="http://192.168.10.103:19999"
# GPU_ID=1

# DATE="2025-06-11"

# echo "$DATE 的時間戳記計算..."
# TIMESTAMP_START=$(TZ=UTC date -d "$DATE 00:00:00" +%s)
# echo "計算時間戳記: $TIMESTAMP_START (UTC)"
# # 計算當天結束時間戳記 (23:59:59)
# TIMESTAMP_END=$(TZ=UTC date -d "$DATE 23:59:59" +%s)
# # 設定數據點間隔為10分鐘，一天共144個點
# POINTS=144



# GPU_UTIL_JSON=$(curl -s "$NETDATA_HOST/api/v1/data?chart=amdgpu.gpu_utilization_unknown_AMD_GPU_card${GPU_ID}&after=$TIMESTAMP_START&before=$TIMESTAMP_END&points=$POINTS&group=average&format=json")
        # 第二步：擷取 VRAM 使用率數據
#VRAM_USAGE_JSON=$(curl -s "$NETDATA_HOST/api/v1/data?chart=amdgpu.gpu_mem_vram_usage_perc_unknown_AMD_GPU_card${GPU_ID}&after=$TIMESTAMP_START&before=$TIMESTAMP_END&points=$POINTS&group=average&format=json")

domain="192.168.10.100"
username="ntnu_ee"
access_token="eyJhbGciOiJIUzI1NiIsImFwaV9hZGRyZXNzIjoiaHR0cDovLzE5Mi4xNjguMTAuMTAwOjgwIiwidHlwIjoiSldUIn0.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0Nzc5NzI3NywianRpIjoiNjUyZDk1ZjEtODU0MC00OTYyLTg4MDItZmJlZGJiMTQyOWFhIiwidHlwZSI6ImFjY2VzcyIsImlkZW50aXR5IjoiYWRtaW4iLCJuYmYiOjE3NDc3OTcyNzcsInJvbGUiOlsiQWRtaW4iXX0.mDdQeARC1MhzAaVik67cKRX4bq8M5C36reUDNWroLd8"

time_start="2025-08-06 00:00:00"
time_end="2025-08-06 23:59:59"
json_file_ntu_ee="ntu_ee_data.json"
json_file="user_data.json"


 curl -G "http://$domain/api/v2/consumption/task" \
   --data-urlencode "start_t=$time_start" \
   --data-urlencode "end_t=$time_end" \
   --data-urlencode "username=$username" \
   -H 'accept: application/json' \
   -H "Authorization: Bearer $access_token" \
   -o "$json_file_ntu_ee"


curl -G "http://$domain/api/v2/consumption/task" \
  --data-urlencode "start_t=$time_start" \
  --data-urlencode "end_t=$time_end" \
  -H 'accept: application/json' \
  -H "Authorization: Bearer $access_token" \
  -o "$json_file"

# echo "=== GPU 卡映射資訊 ==="

# # 方法1: 透過 DRM 裝置
# echo "DRM 裝置:"
# for card in /sys/class/drm/card*; do
#     if [ -d "$card/device" ] && [ -f "$card/device/vendor" ]; then
#         vendor=$(cat "$card/device/vendor" 2>/dev/null)
#         device=$(cat "$card/device/device" 2>/dev/null)
#         if [[ "$vendor" == "0x1002" ]]; then  # AMD vendor ID
#             card_num=$(basename "$card" | sed 's/card//')
#             echo "  card$card_num -> AMD GPU (Vendor: $vendor, Device: $device)"
#         fi
#     fi
# done