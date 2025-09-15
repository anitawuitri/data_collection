# AMD GPU 監控系統 Docker 配置
# 使用多階段構建來優化鏡像大小

# 建構階段
FROM python:3.11-slim as builder

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Poetry
RUN pip install poetry

# 設定工作目錄
WORKDIR /app

# 複製專案配置文件
COPY pyproject.toml poetry.lock* ./

# 配置 Poetry
RUN poetry config virtualenvs.create false

# 安裝依賴 (不含開發依賴)
RUN poetry install --no-dev --extras "full"

# 執行階段
FROM python:3.11-slim

# 安裝執行時系統依賴
RUN apt-get update && apt-get install -y \
    fonts-noto-cjk \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# 創建非 root 使用者
RUN useradd --create-home --shell /bin/bash gpumon

# 設定工作目錄
WORKDIR /app

# 從建構階段複製 Python 環境
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 複製應用程式程式碼
COPY src/ ./src/
COPY README.md ./

# 創建數據和圖表目錄
RUN mkdir -p data plots logs && \
    chown -R gpumon:gpumon /app

# 切換到非 root 使用者
USER gpumon

# 設定環境變數
ENV PYTHONPATH=/app
ENV DATA_DIR=/app/data
ENV PLOTS_DIR=/app/plots
ENV LOG_LEVEL=INFO

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD gpu-monitor status || exit 1

# 設定入口點
ENTRYPOINT ["gpu-monitor"]
CMD ["--help"]