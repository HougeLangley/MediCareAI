#!/bin/bash
# Arch Linux Android 开发环境安装脚本
#  MediCare_AI Mobile App 开发准备

echo "=== MediCareAI - Android 开发环境安装 ==="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}步骤 1: 更新系统${NC}"
sudo pacman -Syu --noconfirm

echo -e "${YELLOW}步骤 2: 安装基础开发工具${NC}"
sudo pacman -S --needed --noconfirm \
    base-devel \
    git \
    curl \
    wget \
    unzip \
    jdk17-openjdk \
    nodejs \
    npm \
    yarn \
    android-tools

echo -e "${YELLOW}步骤 3: 安装 Android Studio${NC}"
# 检查是否已安装
if ! command -v android-studio &> /dev/null; then
    sudo pacman -S --needed --noconfirm android-studio
else
    echo "Android Studio 已安装"
fi

echo -e "${YELLOW}步骤 4: 配置环境变量${NC}"
# 添加到 .bashrc 或 .zshrc
if ! grep -q "ANDROID_HOME" ~/.bashrc; then
    cat >> ~/.bashrc << 'EOF'

# Android 开发环境
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/tools/bin
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin

# Java 环境
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk
export PATH=$PATH:$JAVA_HOME/bin
EOF
    echo "环境变量已添加到 ~/.bashrc"
fi

# 立即生效
source ~/.bashrc 2>/dev/null || source ~/.zshrc 2>/dev/null

echo -e "${YELLOW}步骤 5: 安装 Watchman (React Native 可选)${NC}"
if ! command -v watchman &> /dev/null; then
    # 从 AUR 安装
    if command -v yay &> /dev/null; then
        yay -S --needed --noconfirm watchman
    elif command -v paru &> /dev/null; then
        paru -S --needed --noconfirm watchman
    else
        echo "警告: 未找到 AUR helper，跳过 Watchman 安装"
        echo "React Native 可以正常工作，只是热重载可能稍慢"
    fi
else
    echo "Watchman 已安装"
fi

echo -e "${YELLOW}步骤 6: 安装 React Native CLI${NC}"
npm install -g @react-native-community/cli

echo -e "${YELLOW}步骤 7: 验证安装${NC}"
echo ""
echo "Java 版本:"
java -version 2>&1 | head -1
echo ""
echo "Node.js 版本:"
node --version
echo ""
echo "npm 版本:"
npm --version
echo ""
echo "Android Debug Bridge (adb):"
adb --version 2>&1 | head -1
echo ""

echo -e "${GREEN}=== 安装完成! ===${NC}"
echo ""
echo "下一步:"
echo "1. 启动 Android Studio:  android-studio"
echo "2. 在 Android Studio 中安装 SDK:"
echo "   - Tools → SDK Manager → SDK Platforms"
echo "   - 选择: Android 13.0 (API 33) 或更高"
echo "3. 创建虚拟设备: Tools → Device Manager"
echo "4. 运行: cd /home/houge/Test/MediCareAI && ./setup-mobile-project.sh"
echo ""
echo "注意: 请重新打开终端或运行 'source ~/.bashrc' 使环境变量生效"
