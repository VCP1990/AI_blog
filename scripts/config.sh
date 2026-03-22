#!/bin/bash
# 部署配置文件

# ========== 服务器配置 ==========
SERVER="aliyun"
PROJECT_DIR="/var/www/ai_blog"
SERVICE_NAME="ai_blog"
MAINTENANCE_FILE="$PROJECT_DIR/maintenance/.maintenance"

# ========== 数据库配置 ==========
DB_NAME="ai_blog"
DB_USER="ai_blog"
DB_PASS="AiBlog@2026#Secure"
DB_BACKUP_DIR="/tmp"

# ========== 虚拟环境 ==========
VENV_PATH="$PROJECT_DIR/venv"
VENV_ACTIVATE="$VENV_PATH/bin/activate"

# ========== Django 配置 ==========
DJANGO_SETTINGS="config.settings.production"

# ========== 颜色输出 ==========
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'
