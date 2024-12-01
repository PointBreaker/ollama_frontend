# Ollama Chat Frontend

一个基于 Streamlit 的 Ollama 聊天前端界面，支持多模型选择、SVG 渲染和聊天历史管理。

## 功能特性

- 🤖 支持多模型切换
- 🎨 自动渲染 SVG 图形
- 💾 聊天历史持久化
- 📤 导出聊天记录
- 🔄 流式响应输出
- 🌐 自定义服务器地址

## 快速开始

### 前提条件

- 安装 Docker 和 Docker Compose
- 安装并运行 Ollama 服务
- 确保已安装所需的模型（例如：qwen）

### 本地开发环境

1. 克隆仓库并进入目录：
```bash
git clone <repository-url>
cd ollama-chat
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行应用：
```bash
streamlit run app.py
```

### Docker 部署

1. 使用 host 网络模式（推荐）：
```bash
docker-compose -f docker-compose-host.yml up --build
```

2. 或使用桥接网络模式：
```bash
docker-compose -f docker-compose-bridge.yml up --build
```

## 配置文件

### docker-compose-host.yml
```yaml
services:
  chat-frontend:
    build: .
    network_mode: "host"
    volumes:
      - ./chat_history.db:/app/chat_history.db
      - ./exports:/app/exports
    environment:
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
      - OLLAMA_HOST=localhost
```

## 目录结构

```
ollama-chat/
├── app.py               # 主应用文件
├── db_models.py         # 数据库模型
├── utils.py            # 工具函数
├── requirements.txt     # 项目依赖
├── Dockerfile          # Docker 配置文件
├── docker-compose-host.yml    # Host 网络模式配置
├── docker-compose-bridge.yml  # Bridge 网络模式配置
├── chat_history.db     # SQLite 数据库文件
└── exports/            # 导出文件目录
```

## 环境变量

| 变量名 | 描述 | 默认值 |
|--------|------|---------|
| STREAMLIT_SERVER_PORT | Streamlit 服务端口 | 8501 |
| STREAMLIT_SERVER_ADDRESS | Streamlit 服务地址 | 0.0.0.0 |
| OLLAMA_HOST | Ollama 服务地址 | localhost |

## 使用说明

1. 启动服务后，在浏览器中访问：
   - 本地开发：http://localhost:8501
   - Docker 部署：http://localhost:8501

2. 在侧边栏选择模型：
   - 支持所有已安装的 Ollama 模型
   - 可随时切换模型（会清空当前对话）

3. 聊天功能：
   - 在输入框中输入消息并发送
   - 支持代码和 SVG 渲染
   - 实时流式响应

4. 历史记录：
   - 自动保存所有对话
   - 可浏览历史对话
   - 支持导出对话记录

## 故障排除

1. 无法访问前端界面
   - 检查 8501 端口是否被占用
   - 确认防火墙设置
   ```bash
   netstat -tulpn | grep 8501
   ```

2. 无法连接到 Ollama
   - 确认 Ollama 服务正在运行
   - 检查服务地址配置
   ```bash
   curl http://localhost:11434/api/tags
   ```

3. Docker 连接问题
   - 使用 docker logs 查看日志
   ```bash
   docker logs chat-frontend
   ```

## 维护和更新

1. 更新代码：
```bash
git pull
docker-compose down
docker-compose up --build
```

2. 清理数据：
```bash
rm chat_history.db
rm -rf exports/*
```

## 许可证

MIT License

## 贡献指南

欢迎提交 Issue 和 Pull Request！