# app.py
import os
import streamlit as st
import requests
import json
import time
import re
from typing import List, Dict
from bs4 import BeautifulSoup
from db_models import ChatDatabase
from utils import generate_conversation_title, get_export_path, format_timestamp

# 获取环境变量中的 OLLAMA_HOST，默认为 localhost
DEFAULT_OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'localhost')

# 修改初始化服务器URL的部分
if "server_url" not in st.session_state:
    st.session_state.server_url = f"{DEFAULT_OLLAMA_HOST}:11434"
# 设置页面配置
st.set_page_config(
    page_title="Ollama Chat",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_model" not in st.session_state:
    st.session_state.current_model = None
if "server_url" not in st.session_state:
    st.session_state.server_url = "localhost:11434"
if "db" not in st.session_state:
    st.session_state.db = ChatDatabase()
if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None

def convert_svg_to_html(svg_code: str) -> str:
    """将SVG代码转换为HTML显示格式"""
    try:
        soup = BeautifulSoup(svg_code, 'xml')
        svg = soup.find('svg')
        if svg:
            if not svg.get('viewBox'):
                width = svg.get('width', '800')
                height = svg.get('height', '600')
                svg['viewBox'] = f"0 0 {width} {height}"
            return f'<div class="rendered-svg" style="background-color: white; padding: 10px; border-radius: 5px; margin: 10px 0;">{str(svg)}</div>'
    except Exception:
        pass
    return svg_code

def process_code_blocks(text: str) -> str:
    """处理代码块中的SVG"""
    def replace_svg_in_block(match):
        code_block = match.group(1)
        if code_block.strip().startswith('<svg') and code_block.strip().endswith('</svg>'):
            return convert_svg_to_html(code_block)
        return f"```{code_block}```"

    text = re.sub(r'```(?:svg|xml)\s*([\s\S]*?)```', replace_svg_in_block, text)
    text = re.sub(r'```([\s\S]*?)```', replace_svg_in_block, text)
    return text

def process_inline_svg(text: str) -> str:
    """处理行内SVG标签"""
    def replace_svg(match):
        return convert_svg_to_html(match.group(0))
    return re.sub(r'<svg[\s\S]*?</svg>', replace_svg, text)

def process_message(text: str) -> str:
    """处理消息中的所有SVG内容"""
    text = process_code_blocks(text)
    text = process_inline_svg(text)
    return text

def get_models() -> List[str]:
    """获取所有可用的模型列表"""
    try:
        response = requests.get(f"http://{st.session_state.server_url}/api/tags")
        response.raise_for_status()
        models = response.json().get("models", [])
        return [model["name"] for model in models]
    except requests.exceptions.RequestException as e:
        st.error(f"获取模型列表失败: {str(e)}")
        return []

def send_message(message: str, history: List[Dict], model: str):
    """发送消息到 Ollama API 并获取响应"""
    url = f"http://{st.session_state.server_url}/api/chat"
    messages = [{"role": msg["role"], "content": msg["content"]} for msg in history]
    messages.append({"role": "user", "content": message})
    
    try:
        response = requests.post(
            url,
            json={
                "model": model,
                "messages": messages,
                "stream": True
            },
            stream=True,
            timeout=60
        )
        response.raise_for_status()
        
        full_response = ""
        for line in response.iter_lines():
            if line:
                try:
                    json_response = json.loads(line)
                    if "message" in json_response and "content" in json_response["message"]:
                        chunk = json_response["message"]["content"]
                        full_response += chunk
                        processed_response = process_message(full_response)
                        yield processed_response, False
                except json.JSONDecodeError:
                    continue
        
        final_response = process_message(full_response)
        yield final_response, True
                
    except requests.exceptions.RequestException as e:
        st.error(f"发送消息时出错: {str(e)}")
        yield None, True

def start_new_conversation():
    """开始新对话"""
    st.session_state.messages = []
    st.session_state.current_conversation_id = None
    st.rerun()

# 侧边栏
with st.sidebar:
    st.header("💬 聊天设置")
    
    # 服务器URL设置
    server_url = st.text_input(
        "服务器地址",
        value=st.session_state.server_url,
        help="输入 Ollama 服务器地址，格式如: localhost:11434"
    )
    
    if server_url != st.session_state.server_url:
        st.session_state.server_url = server_url
        st.session_state.current_model = None
        st.rerun()
    
    # 模型选择
    available_models = get_models()
    if available_models:
        if st.session_state.current_model is None:
            st.session_state.current_model = available_models[0]
        
        selected_model = st.selectbox(
            "选择模型",
            available_models,
            index=available_models.index(st.session_state.current_model)
        )
        
        if selected_model != st.session_state.current_model:
            st.session_state.current_model = selected_model
            start_new_conversation()
    else:
        st.error("无法获取模型列表，请检查服务器地址是否正确")
    
    # 历史对话
    st.markdown("---")
    st.subheader("📚 历史对话")
    
    # 新对话按钮
    if st.button("➕ 新对话"):
        start_new_conversation()
    
    # 显示历史对话列表
    conversations = st.session_state.db.get_all_conversations()
    for conv_id, title, model, created_at in conversations:
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(f"📝 {title}", key=f"conv_{conv_id}"):
                conv_data = st.session_state.db.get_conversation(conv_id)
                st.session_state.messages = conv_data["messages"]
                st.session_state.current_model = conv_data["model"]
                st.session_state.current_conversation_id = conv_id
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{conv_id}"):
                st.session_state.db.delete_conversation(conv_id)
                if conv_id == st.session_state.current_conversation_id:
                    start_new_conversation()
                else:
                    st.rerun()
    
    # 导出当前对话
    if st.session_state.current_conversation_id:
        st.markdown("---")
        if st.button("💾 导出当前对话"):
            export_path = get_export_path("exports", st.session_state.current_conversation_id)
            st.session_state.db.export_conversation(st.session_state.current_conversation_id, export_path)
            st.success(f"对话已导出到: {export_path}")

# 主界面
st.title("🤖 Ollama Chat")

if not st.session_state.current_model:
    st.warning("请先在左侧选择一个模型")
else:
    # 显示聊天历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)

    # 聊天输入
    if prompt := st.chat_input("输入您的消息..."):
        # 显示用户消息
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 创建新对话或添加到现有对话
        if not st.session_state.current_conversation_id:
            title = generate_conversation_title(prompt)
            st.session_state.current_conversation_id = st.session_state.db.create_conversation(
                title, 
                st.session_state.current_model
            )
        
        # 保存用户消息
        st.session_state.db.add_message(
            st.session_state.current_conversation_id,
            "user",
            prompt
        )
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # 显示助手消息
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            response_complete = False
            final_response = None
            
            for response_chunk, is_complete in send_message(prompt, st.session_state.messages, st.session_state.current_model):
                if response_chunk is not None:
                    message_placeholder.markdown(response_chunk + "▌", unsafe_allow_html=True)
                    time.sleep(0.01)
                response_complete = is_complete
                if is_complete:
                    final_response = response_chunk
            
            if response_complete and final_response is not None:
                message_placeholder.markdown(final_response, unsafe_allow_html=True)
                # 保存助手消息
                st.session_state.db.add_message(
                    st.session_state.current_conversation_id,
                    "assistant",
                    final_response
                )
                st.session_state.messages.append({"role": "assistant", "content": final_response})
            elif not response_complete:
                message_placeholder.markdown("❌ 获取响应失败，请检查服务器连接。")

# 添加自定义 CSS
st.markdown("""
<style>
    .rendered-svg {
        display: block !important;
    }
    .rendered-svg svg {
        max-width: 100%;
        height: auto;
    }
</style>
""", unsafe_allow_html=True)