#!/usr/bin/env python3
"""
学术论文辅助平台统一启动脚本
同时启动后端FastAPI服务和前端Vue开发服务器
"""

import os
import sys
import subprocess
import platform
import time
import signal
import argparse
from pathlib import Path

# 颜色定义
class Colors:
    GREEN = '\033[0;32m'
    BLUE = '\033[0;34m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m'  # No Color

# 打印带颜色的信息
def print_info(message):
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")

def print_success(message):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")

def print_warning(message):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")

def print_error(message):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")

# 获取项目根目录
def get_project_root():
    return Path(__file__).parent.absolute()

# 检查是否安装了必要的工具
def check_requirements():
    print_info("检查必要的工具...")

    # 检查Node.js
    try:
        subprocess.run(["node", "--version"], check=True, capture_output=True)
    except:
        print_error("未找到Node.js，请安装Node.js")
        sys.exit(1)

    # 检查npm
    try:
        subprocess.run(["npm", "--version"], check=True, capture_output=True)
    except:
        print_error("未找到npm，请安装npm")
        sys.exit(1)

    print_success("所有必要的工具已安装")

# 安装后端依赖
def install_backend_deps(venv_path=None):
    print_info("安装后端依赖...")

    root_dir = get_project_root()
    backend_dir = os.path.join(root_dir, "backend")

    # 构建命令
    if venv_path:
        # 使用指定的虚拟环境
        if platform.system() == "Windows":
            pip_cmd = os.path.join(venv_path, "Scripts", "pip")
        else:
            pip_cmd = os.path.join(venv_path, "bin", "pip")
    else:
        # 使用系统Python
        pip_cmd = [sys.executable, "-m", "pip"]

    # 安装依赖
    try:
        if isinstance(pip_cmd, list):
            cmd = pip_cmd + ["install", "-r", os.path.join(backend_dir, "requirements.txt")]
        else:
            cmd = [pip_cmd, "install", "-r", os.path.join(backend_dir, "requirements.txt")]

        subprocess.run(cmd, check=True)
        print_success("后端依赖安装成功")
    except subprocess.CalledProcessError:
        print_error("后端依赖安装失败")
        sys.exit(1)

# 安装前端依赖
def install_frontend_deps():
    print_info("安装前端依赖...")

    root_dir = get_project_root()
    frontend_dir = os.path.join(root_dir, "frontend")

    # 安装依赖
    try:
        subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
        print_success("前端依赖安装成功")
    except subprocess.CalledProcessError:
        print_error("前端依赖安装失败")
        sys.exit(1)

# 启动后端服务
def start_backend(venv_path=None, port=8000):
    print_info(f"启动后端服务，端口: {port}...")

    root_dir = get_project_root()
    backend_dir = os.path.join(root_dir, "backend")

    # 构建命令
    if venv_path:
        # 使用指定的虚拟环境
        if platform.system() == "Windows":
            python_cmd = os.path.join(venv_path, "Scripts", "python")
        else:
            python_cmd = os.path.join(venv_path, "bin", "python")
    else:
        # 使用系统Python
        python_cmd = sys.executable

    # 启动后端服务
    cmd = [python_cmd, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", str(port)]
    backend_process = subprocess.Popen(cmd, cwd=backend_dir)

    print_success(f"后端服务已启动，PID: {backend_process.pid}")
    return backend_process

# 启动前端服务
def start_frontend(port=3000):
    print_info(f"启动前端服务，端口: {port}...")

    root_dir = get_project_root()
    frontend_dir = os.path.join(root_dir, "frontend")

    # 启动前端服务
    env = os.environ.copy()
    env["PORT"] = str(port)
    frontend_process = subprocess.Popen(["npm", "run", "dev"], cwd=frontend_dir, env=env)

    print_success(f"前端服务已启动，PID: {frontend_process.pid}")
    return frontend_process

# 清理函数
def cleanup(backend_process, frontend_process):
    print_info("正在关闭服务...")

    # 关闭后端进程
    if backend_process:
        backend_process.terminate()
        try:
            backend_process.wait(timeout=5)
            print_success("后端服务已关闭")
        except subprocess.TimeoutExpired:
            backend_process.kill()
            print_warning("后端服务被强制关闭")

    # 关闭前端进程
    if frontend_process:
        frontend_process.terminate()
        try:
            frontend_process.wait(timeout=5)
            print_success("前端服务已关闭")
        except subprocess.TimeoutExpired:
            frontend_process.kill()
            print_warning("前端服务被强制关闭")

    print_success("所有服务已关闭")

# 主函数
def main():
    parser = argparse.ArgumentParser(description="学术论文辅助平台统一启动脚本")
    parser.add_argument("--venv", help="Python虚拟环境路径，如果不指定则使用默认虚拟环境")
    parser.add_argument("--backend-port", type=int, default=8000, help="后端服务端口，默认为8000")
    parser.add_argument("--frontend-port", type=int, default=3000, help="前端服务端口，默认为3000")
    parser.add_argument("--install-deps", action="store_true", help="安装依赖")
    parser.add_argument("--no-deps", action="store_true", help="不安装依赖，直接启动服务")
    args = parser.parse_args()

    # 如果未指定虚拟环境，使用默认的eduvenv
    if not args.venv:
        args.venv = os.path.join(get_project_root(), "eduvenv")

    print("==================================================")
    print("       学术论文辅助平台统一启动脚本")
    print("==================================================")

    # 检查要求
    check_requirements()

    # 安装依赖，仅当显式指定--install-deps时才安装
    if args.install_deps:
        install_backend_deps(args.venv)
        install_frontend_deps()

        # 创建标记文件表示依赖已安装
        with open(os.path.join(get_project_root(), "backend", ".deps_installed"), "w") as f:
            f.write("Dependencies installed on " + time.strftime("%Y-%m-%d %H:%M:%S"))

    # 启动服务
    backend_process = start_backend(args.venv, args.backend_port)
    frontend_process = start_frontend(args.frontend_port)

    print_info("所有服务已启动，按Ctrl+C停止所有服务")

    # 注册信号处理
    def signal_handler(sig, frame):
        cleanup(backend_process, frontend_process)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 保持脚本运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup(backend_process, frontend_process)

if __name__ == "__main__":
    main()
