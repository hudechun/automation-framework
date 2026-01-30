#!/usr/bin/env bash
set -euo pipefail

echo "===== Bun + Oh My OpenCode 自动安装脚本 ====="

install_bun_linux() {
  if command -v bun >/dev/null 2>&1; then
    echo "bun 已安装：$(bun -v)"
    return
  fi
  echo "[Step] 安装 Bun ..."
  curl -fsSL https://bun.sh/install | bash
  export PATH="$HOME/.bun/bin:$PATH"
  if ! command -v bun >/dev/null 2>&1; then
    echo "bun 安装失败，请手动安装或检查网络"
    exit 1
  fi
  echo "bun 安装成功：$(bun -v)"
}

install_oh_my_opencode() {
  if [ ! -d "oh-my-opencode" ]; then
    echo "[Step] 克隆 oh-my-opencode 仓库 ..."
    git clone https://github.com/code-yeongyu/oh-my-opencode.git
  fi
  cd oh-my-opencode
  echo "[Step] 安装依赖 ..."
  if command -v bun >/dev/null 2>&1; then
    bun install || npm install --legacy-peer-deps
  else
    npm install --legacy-peer-deps
  fi
  if [ -f "package.json" ]; then
    echo "[Step] 构建插件 ..."
    if command -v bun >/dev/null 2>&1; then
      bun run build || bun run build:schema || npm run build
    else
      npm run build || echo "无可用构建脚本，跳过"
    fi
  fi
  echo "[完成] Oh My OpenCode 安装完成（依赖已安装，构建状态以输出为准）"
}

if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
  install_bun_linux
  install_oh_my_opencode
else
  echo "当前系统为 Windows。请通过 Windows 子系统 Linux (WSL) 来执行本脚本："
  echo "1) 安装 WSL 与一个 Linux 发行版 (如 Ubuntu)"
  echo "2) 在 WSL 中执行："
  echo "   git clone https://github.com/code-yeongyu/oh-my-opencode.git"
  echo "   cd oh-my-opencode"
  echo "   bash scripts/setup-bun-and-oh-my-opencode.sh"
fi
