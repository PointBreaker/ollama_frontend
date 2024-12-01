FROM python:3.9-slim

WORKDIR /app

# 复制所需文件
COPY requirements.txt .
COPY app.py .
COPY db_models.py .
COPY utils.py .

# 创建必要的目录
RUN mkdir -p exports

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置环境变量
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS="0.0.0.0"
# 禁用 Streamlit 的文件监视功能，这在容器中可能导致问题
ENV STREAMLIT_SERVER_FILE_WATCHER_TYPE="none"
# 允许跨域请求
ENV STREAMLIT_SERVER_ENABLE_CORS=true

# 暴露端口
EXPOSE 8501

# 启动应用
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]