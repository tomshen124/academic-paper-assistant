#!/bin/bash

# 检测是否安装了uv
if command -v uv &> /dev/null; then
    echo "使用uv安装依赖..."
    
    # 创建虚拟环境（如果不存在）
    if [ ! -d "eduvenv" ]; then
        echo "创建虚拟环境..."
        uv venv
    fi
    
    # 安装依赖
    echo "安装依赖..."
    uv pip install -e .
    
    echo "依赖安装完成！"
else
    echo "未检测到uv，使用pip安装依赖..."
    
    # 检查是否已经存在虚拟环境
    if [ ! -d "eduvenv" ]; then
        echo "创建虚拟环境..."
        python3 -m venv eduvenv
    fi
    
    # 激活虚拟环境
    source eduvenv/bin/activate
    
    # 升级pip
    pip install --upgrade pip
    
    # 安装依赖
    echo "安装依赖..."
    pip install -r requirements.txt
    
    echo "依赖安装完成！"
fi
