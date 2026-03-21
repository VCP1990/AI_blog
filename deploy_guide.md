# AI Blog 部署指南

本文档详细介绍如何将 AI Blog 项目从本地上传到 GitHub，并部署到阿里云 Ubuntu 服务器。

---

## 目录

1. [部署架构](#部署架构)
2. [第一阶段：GitHub 上传](#第一阶段github-上传)
3. [第二阶段：服务器环境准备](#第二阶段服务器环境准备)
4. [第三阶段：项目部署](#第三阶段项目部署)
5. [第四阶段：Gunicorn 配置](#第四阶段gunicorn-配置)
6. [第五阶段：Nginx 配置](#第五阶段nginx-配置)
7. [第六阶段：SSL 证书](#第六阶段ssl-证书)
8. [第七阶段：自动备份](#第七阶段自动备份)
9. [第八阶段：安全加固](#第八阶段安全加固)
10. [日常维护](#日常维护)
11. [常见问题](#常见问题)

---

## 部署架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户请求                                  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Nginx (80/443)                               │
│  - 静态文件服务 (/static/, /media/)                              │
│  - 反向代理到 Gunicorn                                           │
│  - SSL 终止                                                      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Gunicorn (127.0.0.1:8000)                      │
│  - WSGI 服务器                                                   │
│  - 多进程处理请求                                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Django 应用                                   │
│  - 业务逻辑处理                                                   │
│  - 模板渲染                                                       │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MySQL 数据库                                  │
│  - 数据持久化存储                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 第一阶段：GitHub 上传

### 1.1 在 GitHub 创建仓库

1. 登录 [GitHub](https://github.com)
2. 点击右上角 `+` → `New repository`
3. 填写信息：
   - Repository name: `ai_blog`
   - Description: `AI Blog - Django + Tailwind CSS`
   - 选择 `Private` 或 `Public`
   - **不要**勾选 "Add a README file"
4. 点击 `Create repository`

### 1.2 本地 Git 初始化

在项目根目录执行：

```bash
# 初始化 Git 仓库
git init

# 添加所有文件
git add .

# 首次提交
git commit -m "Initial commit: AI Blog project"

# 关联远程仓库（替换为你的用户名）
git remote add origin https://github.com/YOUR_USERNAME/ai_blog.git

# 设置默认分支
git branch -M main

# 推送到 GitHub
git push -u origin main
```

### 1.3 验证上传成功

访问 `https://github.com/YOUR_USERNAME/ai_blog` 确认代码已上传。

---

## 第二阶段：服务器环境准备

### 2.1 连接服务器

```bash
ssh root@your-server-ip
```

### 2.2 更新系统

```bash
sudo apt update && sudo apt upgrade -y
```

### 2.3 安装系统依赖

```bash
sudo apt install -y \
    python3-pip \
    python3-venv \
    nginx \
    mysql-server \
    libmysqlclient-dev \
    pkg-config \
    git \
    curl \
    wget
```

### 2.4 安装 Certbot (SSL 证书工具)

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 2.5 配置防火墙

```bash
# 允许必要端口
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'

# 启用防火墙
sudo ufw enable

# 查看状态
sudo ufw status
```

---

## 第三阶段：项目部署

### 3.1 MySQL 配置

```bash
# 登录 MySQL
sudo mysql

# 在 MySQL 命令行中执行：
```

```sql
-- 创建数据库
CREATE DATABASE ai_blog CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户（替换密码）
CREATE USER 'ai_blog'@'localhost' IDENTIFIED BY 'YOUR_STRONG_PASSWORD_HERE';

-- 授权
GRANT ALL PRIVILEGES ON ai_blog.* TO 'ai_blog'@'localhost';

-- 刷新权限
FLUSH PRIVILEGES;

-- 退出
EXIT;
```

### 3.2 创建项目目录

```bash
# 创建目录
sudo mkdir -p /var/www/ai_blog

# 设置所有者（替换为你的用户名）
sudo chown $USER:$USER /var/www/ai_blog
```

### 3.3 克隆项目

```bash
# 进入目录
cd /var/www/ai_blog

# 克隆项目（替换为你的仓库地址）
git clone https://github.com/YOUR_USERNAME/ai_blog.git .

# 如果是私有仓库，需要配置 SSH Key 或 Personal Access Token
```

### 3.4 创建虚拟环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
```

### 3.5 配置环境变量

```bash
# 复制示例文件
cp .env.example .env

# 编辑配置
nano .env
```

修改 `.env` 文件内容：

```env
# 生产环境配置
DJANGO_ENVIRONMENT=production

# 生成密钥：python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
DJANGO_SECRET_KEY=your-generated-secret-key-here

# 你的域名（多个用逗号分隔）
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com,your-server-ip

# MySQL 配置
DB_NAME=ai_blog
DB_USER=ai_blog
DB_PASSWORD=YOUR_MYSQL_PASSWORD_HERE
DB_HOST=localhost
DB_PORT=3306

# 邮件配置（可选）
EMAIL_HOST=smtp.qq.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@qq.com
EMAIL_HOST_PASSWORD=your-email-password
```

生成密钥：

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3.6 数据库迁移和静态文件

```bash
# 确保在虚拟环境中
source venv/bin/activate

# 设置环境变量
export DJANGO_ENVIRONMENT=production

# 数据库迁移
python manage.py migrate

# 收集静态文件
python manage.py collectstatic --noinput

# 创建管理员账号
python manage.py createsuperuser
```

### 3.7 设置目录权限

```bash
# 设置 media 目录权限（用于上传文件）
sudo chown -R www-data:www-data /var/www/ai_blog/media
sudo chmod -R 755 /var/www/ai_blog/media

# 设置 staticfiles 目录权限
sudo chown -R www-data:www-data /var/www/ai_blog/staticfiles
sudo chmod -R 755 /var/www/ai_blog/staticfiles
```

---

## 第四阶段：Gunicorn 配置

### 4.1 创建 Systemd 服务

```bash
sudo nano /etc/systemd/system/ai_blog.service
```

写入以下内容：

```ini
[Unit]
Description=AI Blog Gunicorn Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/ai_blog
Environment="PATH=/var/www/ai_blog/venv/bin"
Environment="DJANGO_ENVIRONMENT=production"
ExecStart=/var/www/ai_blog/venv/bin/gunicorn --config gunicorn.conf.py config.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillSignal=SIGQUIT
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 4.2 启动服务

```bash
# 重新加载 systemd 配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start ai_blog

# 设置开机自启
sudo systemctl enable ai_blog

# 查看状态
sudo systemctl status ai_blog

# 查看日志
sudo journalctl -u ai_blog -f
```

---

## 第五阶段：Nginx 配置

### 5.1 创建 Nginx 配置文件

```bash
sudo nano /etc/nginx/sites-available/ai_blog
```

写入以下内容（替换域名）：

```nginx
upstream ai_blog {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    listen [::]:80;
    server_name your-domain.com www.your-domain.com;

    # 文件上传大小限制
    client_max_body_size 20M;

    # 静态文件
    location /static/ {
        alias /var/www/ai_blog/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # 媒体文件
    location /media/ {
        alias /var/www/ai_blog/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    # favicon
    location = /favicon.ico {
        alias /var/www/ai_blog/staticfiles/favicon.ico;
        log_not_found off;
    }

    # 代理到 Gunicorn
    location / {
        proxy_pass http://ai_blog;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_read_timeout 60s;
        proxy_send_timeout 60s;
    }
}
```

### 5.2 启用站点配置

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/ai_blog /etc/nginx/sites-enabled/

# 删除默认配置
sudo rm /etc/nginx/sites-enabled/default

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx

# 查看状态
sudo systemctl status nginx
```

### 5.3 验证 HTTP 访问

此时访问 `http://your-domain.com` 应该可以看到网站（无 HTTPS）。

---

## 第六阶段：SSL 证书

### 6.1 申请 Let's Encrypt 证书

```bash
# 申请证书（替换域名）
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

按提示操作：
1. 输入邮箱地址
2. 同意服务条款
3. 选择是否重定向 HTTP 到 HTTPS（推荐选择 `2` - 重定向）

### 6.2 验证 HTTPS

访问 `https://your-domain.com` 确认证书生效。

### 6.3 设置自动续期

```bash
# 测试自动续期
sudo certbot renew --dry-run

# Certbot 会自动添加定时任务，无需手动配置
```

---

## 第七阶段：自动备份

本阶段配置自动备份，将数据库和媒体文件备份到阿里云 OSS。

### 7.1 创建 OSS Bucket

1. 登录 [阿里云 OSS 控制台](https://oss.console.aliyun.com/)
2. 点击 `创建 Bucket`
3. 配置：
   - Bucket 名称：`ai-blog-backup`
   - 地域：选择与服务器相同的地域（如华东1-杭州）
   - 存储类型：标准存储
   - 读写权限：私有
4. 点击 `确定` 创建

### 7.2 创建 RAM 用户和 AccessKey

1. 进入 [RAM 访问控制](https://ram.console.aliyun.com/)
2. 创建用户：
   - 用户名：`ai-blog-backup`
   - 访问方式：勾选 `OpenAPI 调用访问`
3. 创建成功后，**立即保存 AccessKey ID 和 Secret**（只显示一次）
4. 添加权限：`AliyunOSSFullAccess`（或创建自定义策略只允许访问特定 Bucket）

### 7.3 安装 ossutil 工具

```bash
# 下载 ossutil
wget https://gosspublic.alicdn.com/ossutil/1.7.15/ossutil64

# 添加执行权限
chmod 755 ossutil64

# 移动到系统目录
sudo mv ossutil64 /usr/local/bin/ossutil

# 验证安装
ossutil --version
```

### 7.4 配置 ossutil

```bash
# 交互式配置
ossutil config

# 按提示输入：
# - Endpoint: oss-cn-hangzhou.aliyuncs.com（根据你的 Bucket 地域）
# - AccessKeyID: 你的 AccessKey ID
# - AccessKeySecret: 你的 AccessKey Secret
# - STSToken: 直接回车跳过
```

或手动创建配置文件：

```bash
sudo nano /root/.ossutilconfig
```

写入以下内容：

```ini
[Credentials]
language=CH
endpoint=oss-cn-hangzhou.aliyuncs.com
accessKeyID=YOUR_ACCESS_KEY_ID
accessKeySecret=YOUR_ACCESS_KEY_SECRET
```

测试连接：

```bash
# 列出 Bucket（验证配置）
ossutil ls

# 应该能看到你创建的 Bucket
```

### 7.5 创建备份脚本

```bash
# 创建脚本目录
sudo mkdir -p /var/www/ai_blog/scripts

# 创建备份脚本
sudo nano /var/www/ai_blog/scripts/backup.sh
```

写入以下内容：

```bash
#!/bin/bash

# ============================================
# AI Blog 自动备份脚本
# 功能：备份 MySQL 数据库和 media 文件到 OSS
# ============================================

# 配置区域
# --------------------------------------------
DB_NAME="ai_blog"
DB_USER="ai_blog"
DB_PASS="YOUR_MYSQL_PASSWORD"  # 替换为你的数据库密码

PROJECT_DIR="/var/www/ai_blog"
MEDIA_DIR="${PROJECT_DIR}/media"
BACKUP_DIR="/tmp/ai_blog_backup"

OSS_BUCKET="oss://ai-blog-backup"  # 替换为你的 Bucket 名称
RETENTION_DAYS=7  # 保留天数

# 日期变量
DATE=$(date +%Y%m%d)
DATETIME=$(date +%Y%m%d_%H%M%S)

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 创建备份目录
mkdir -p ${BACKUP_DIR}

# ============================================
# 1. 备份 MySQL 数据库
# ============================================
log "开始备份数据库..."

DB_BACKUP_FILE="${BACKUP_DIR}/db_${DATETIME}.sql.gz"

mysqldump -u${DB_USER} -p${DB_PASS} ${DB_NAME} 2>/dev/null | gzip > ${DB_BACKUP_FILE}

if [ $? -eq 0 ]; then
    log "数据库备份成功: ${DB_BACKUP_FILE}"
    
    # 上传到 OSS
    ossutil cp ${DB_BACKUP_FILE} ${OSS_BUCKET}/db/ -f
    if [ $? -eq 0 ]; then
        log "数据库已上传到 OSS"
    else
        log "ERROR: 数据库上传 OSS 失败"
    fi
else
    log "ERROR: 数据库备份失败"
fi

# ============================================
# 2. 备份 media 目录
# ============================================
log "开始备份 media 目录..."

if [ -d "${MEDIA_DIR}" ] && [ "$(ls -A ${MEDIA_DIR} 2>/dev/null)" ]; then
    MEDIA_BACKUP_FILE="${BACKUP_DIR}/media_${DATETIME}.tar.gz"
    
    tar -czf ${MEDIA_BACKUP_FILE} -C ${PROJECT_DIR} media
    
    if [ $? -eq 0 ]; then
        log "Media 备份成功: ${MEDIA_BACKUP_FILE}"
        
        # 上传到 OSS
        ossutil cp ${MEDIA_BACKUP_FILE} ${OSS_BUCKET}/media/ -f
        if [ $? -eq 0 ]; then
            log "Media 已上传到 OSS"
        else
            log "ERROR: Media 上传 OSS 失败"
        fi
    else
        log "ERROR: Media 打包失败"
    fi
else
    log "WARNING: media 目录为空或不存在，跳过备份"
fi

# ============================================
# 3. 清理旧备份
# ============================================
log "清理 ${RETENTION_DAYS} 天前的旧备份..."

# 计算 cutoff 日期
CUTOFF_DATE=$(date -d "-${RETENTION_DAYS} days" +%Y%m%d)

# 清理 OSS 上的旧备份
ossutil ls ${OSS_BUCKET}/db/ | while read line; do
    FILE_DATE=$(echo $line | grep -oP '\d{8}' | head -1)
    if [ -n "$FILE_DATE" ] && [ "$FILE_DATE" -lt "$CUTOFF_DATE" ]; then
        ossutil rm $(echo $line | awk '{print $NF}') -f
        log "已删除旧备份: $(echo $line | awk '{print $NF}')"
    fi
done

# 清理本地临时文件
rm -f ${BACKUP_DIR}/*.sql.gz ${BACKUP_DIR}/*.tar.gz

log "备份完成！"
```

设置权限：

```bash
# 设置脚本权限
sudo chmod 700 /var/www/ai_blog/scripts/backup.sh

# 设置所有者
sudo chown root:root /var/www/ai_blog/scripts/backup.sh
```

### 7.6 配置定时任务

```bash
# 编辑 crontab
sudo crontab -e

# 添加以下内容（每天凌晨 3:00 执行备份）
0 3 * * * /var/www/ai_blog/scripts/backup.sh >> /var/log/ai_blog_backup.log 2>&1
```

### 7.7 测试备份

```bash
# 手动执行备份脚本
sudo /var/www/ai_blog/scripts/backup.sh

# 查看日志
cat /var/log/ai_blog_backup.log

# 检查 OSS 上的备份文件
ossutil ls oss://ai-blog-backup/db/
ossutil ls oss://ai-blog-backup/media/
```

### 7.8 数据恢复

#### 恢复数据库

```bash
# 从 OSS 下载备份
ossutil cp oss://ai-blog-backup/db/db_20260316_030000.sql.gz /tmp/

# 解压
gunzip /tmp/db_20260316_030000.sql.gz

# 恢复数据库（警告：会覆盖现有数据）
mysql -u ai_blog -p ai_blog < /tmp/db_20260316_030000.sql
```

#### 恢复 media 文件

```bash
# 从 OSS 下载备份
ossutil cp oss://ai-blog-backup/media/media_20260316_030000.tar.gz /tmp/

# 解压到项目目录
tar -xzf /tmp/media_20260316_030000.tar.gz -C /var/www/ai_blog/

# 修复权限
sudo chown -R www-data:www-data /var/www/ai_blog/media
```

### 7.9 备份成本估算

| 项目 | 用量 | 单价 | 月费用 |
|------|------|------|--------|
| OSS 存储 | ~5GB | 0.12元/GB | ~0.6元 |
| 上传流量 | 备份上传免费 | - | 0元 |
| 请求次数 | 较少 | 极低 | ~0.1元 |
| **合计** | | | **~1元/月** |

---

## 第八阶段：安全加固

### 8.1 SSH 安全加固

```bash
# 备份配置文件
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak

# 编辑配置
sudo nano /etc/ssh/sshd_config
```

修改以下配置：

```bash
# 修改默认端口（可选，改为非常用端口）
Port 2222

# 禁用 root 登录
PermitRootLogin no

# 禁用密码登录（配置 SSH Key 后启用）
PasswordAuthentication no

# 限制登录尝试
MaxAuthTries 3

# 空闲超时断开（秒）
ClientAliveInterval 300
ClientAliveCountMax 2

# 只允许特定用户登录（可选）
AllowUsers your_username
```

**重要**：修改端口后需要更新防火墙：

```bash
# 允许新端口
sudo ufw allow 2222/tcp

# 重新加载 SSH 配置
sudo systemctl reload sshd

# 测试新端口连接（保持当前连接，新开终端测试）
ssh -p 2222 your_username@your-server-ip
```

### 8.2 SSH Key 配置（推荐）

**本地生成密钥（Windows PowerShell）：**

```powershell
# 生成 ED25519 密钥（推荐）
ssh-keygen -t ed25519 -C "your_email@example.com"

# 查看公钥
cat ~/.ssh/id_ed25519.pub
```

**服务器配置公钥：**

```bash
# 创建 .ssh 目录
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# 添加公钥
nano ~/.ssh/authorized_keys
# 粘贴公钥内容

# 设置权限
chmod 600 ~/.ssh/authorized_keys
```

### 8.3 防火墙精细配置

```bash
# 重置防火墙规则
sudo ufw --force reset

# 默认策略
sudo ufw default deny incoming
sudo ufw default allow outgoing

# 允许 SSH（根据你的端口）
sudo ufw allow 2222/tcp comment 'SSH'

# 允许 HTTP 和 HTTPS
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'

# 限制连接频率（防暴力破解）
sudo ufw limit 2222/tcp

# 启用防火墙
sudo ufw enable

# 查看状态
sudo ufw status numbered
```

### 8.4 数据库安全

```bash
# 登录 MySQL
sudo mysql

# 执行以下安全配置
```

```sql
-- 删除匿名用户
DELETE FROM mysql.user WHERE User='';

-- 禁止 root 远程登录
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');

-- 删除测试数据库
DROP DATABASE IF EXISTS test;

-- 刷新权限
FLUSH PRIVILEGES;
```

运行 MySQL 安全脚本：

```bash
sudo mysql_secure_installation
```

按提示操作：
- 设置密码验证策略：`N`（或根据需求选择）
- 设置 root 密码：如果之前没设置
- 移除匿名用户：`Y`
- 禁止 root 远程登录：`Y`
- 删除测试数据库：`Y`

### 8.5 环境变量保护

```bash
# 设置 .env 文件权限
sudo chmod 600 /var/www/ai_blog/.env
sudo chown www-data:www-data /var/www/ai_blog/.env

# 验证权限
ls -la /var/www/ai_blog/.env
# 应显示：-rw------- 1 www-data www-data
```

### 8.6 Nginx 安全头

编辑 Nginx 配置：

```bash
sudo nano /etc/nginx/sites-available/ai_blog
```

在 `server` 块内添加安全头：

```nginx
server {
    # ... 现有配置 ...

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;

    # 隐藏 Nginx 版本
    server_tokens off;

    # ... 其余配置 ...
}
```

重新加载 Nginx：

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 8.7 系统自动更新

```bash
# 安装无人值守更新
sudo apt install -y unattended-upgrades

# 配置自动更新
sudo dpkg-reconfigure -plow unattended-upgrades
# 选择 "Yes"

# 编辑配置（可选）
sudo nano /etc/apt/apt.conf.d/50unattended-upgrades
```

启用自动安全更新：

```bash
sudo nano /etc/apt/apt.conf.d/20auto-upgrades
```

确保包含：

```
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::AutocleanInterval "7";
```

### 8.8 安全检查清单

完成以上配置后，逐项检查：

- [ ] SSH 端口已修改（非 22）
- [ ] root 登录已禁用
- [ ] 密码登录已禁用（使用 SSH Key）
- [ ] 防火墙只开放必要端口
- [ ] MySQL 只监听 localhost
- [ ] `.env` 文件权限为 600
- [ ] Nginx 安全头已配置
- [ ] 自动安全更新已启用

### 8.9 安全验证

```bash
# 检查开放端口
sudo ss -tlnp

# 检查防火墙状态
sudo ufw status

# 检查 SSH 配置
sudo sshd -t

# 检查失败登录尝试（如果有 fail2ban）
sudo fail2ban-client status

# 检查系统更新
apt list --upgradable
```

### 更新代码

```bash
# 进入项目目录
cd /var/www/ai_blog

# 拉取最新代码
git pull origin main

# 激活虚拟环境
source venv/bin/activate

# 更新依赖（如有变更）
pip install -r requirements.txt

# 数据库迁移（如有变更）
python manage.py migrate

# 收集静态文件（如有变更）
python manage.py collectstatic --noinput

# 重启服务
sudo systemctl restart ai_blog
```

### 查看日志

```bash
# Gunicorn 日志
sudo journalctl -u ai_blog -f

# Nginx 访问日志
sudo tail -f /var/log/nginx/access.log

# Nginx 错误日志
sudo tail -f /var/log/nginx/error.log
```

### 重启服务

```bash
# 重启 Gunicorn
sudo systemctl restart ai_blog

# 重启 Nginx
sudo systemctl restart nginx

# 重启所有
sudo systemctl restart ai_blog nginx
```

### 备份数据库

```bash
# 备份 MySQL
mysqldump -u ai_blog -p ai_blog > backup_$(date +%Y%m%d).sql

# 恢复 MySQL
mysql -u ai_blog -p ai_blog < backup_20260316.sql
```

### 备份媒体文件

```bash
# 打包 media 目录
tar -czvf media_backup_$(date +%Y%m%d).tar.gz /var/www/ai_blog/media/
```

---

## 常见问题

### Q1: 502 Bad Gateway

**原因**：Gunicorn 服务未启动或端口不对

**解决**：
```bash
# 检查 Gunicorn 状态
sudo systemctl status ai_blog

# 检查端口
sudo netstat -tlnp | grep 8000

# 重启服务
sudo systemctl restart ai_blog
```

### Q2: 静态文件 404

**原因**：静态文件未收集或 Nginx 配置错误

**解决**：
```bash
# 收集静态文件
python manage.py collectstatic --noinput

# 检查 Nginx 配置
sudo nginx -t

# 检查目录权限
ls -la /var/www/ai_blog/staticfiles/
```

### Q3: 数据库连接失败

**原因**：MySQL 配置错误或权限问题

**解决**：
```bash
# 测试数据库连接
mysql -u ai_blog -p ai_blog

# 检查 .env 配置
cat /var/www/ai_blog/.env
```

### Q4: 媒体文件上传失败

**原因**：目录权限问题

**解决**：
```bash
# 修复权限
sudo chown -R www-data:www-data /var/www/ai_blog/media
sudo chmod -R 755 /var/www/ai_blog/media
```

### Q5: SSL 证书申请失败

**原因**：域名未正确解析到服务器

**解决**：
```bash
# 检查域名解析
dig your-domain.com

# 确保 Nginx 正在运行
sudo systemctl status nginx
```

### Q6: 内存不足

**原因**：服务器内存太小

**解决**：
```bash
# 添加 Swap（临时方案）
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 永久生效
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Q7: 备份脚本执行失败

**原因**：ossutil 配置错误或权限不足

**解决**：
```bash
# 检查 ossutil 配置
ossutil ls

# 检查数据库密码是否正确
mysql -u ai_blog -p

# 手动执行脚本查看详细错误
sudo bash -x /var/www/ai_blog/scripts/backup.sh
```

### Q8: SSH 连接被拒绝

**原因**：修改端口后未更新防火墙或客户端配置

**解决**：
```bash
# 检查 SSH 服务状态
sudo systemctl status sshd

# 检查监听端口
sudo ss -tlnp | grep sshd

# 客户端连接时指定端口
ssh -p 2222 username@your-server-ip
```

### Q9: 如何查看备份日志

**原因**：需要确认备份是否成功

**解决**：
```bash
# 查看备份日志
cat /var/log/ai_blog_backup.log

# 查看 Cron 日志
grep CRON /var/log/syslog | tail -20

# 查看 OSS 上的备份文件
ossutil ls oss://ai-blog-backup/db/
ossutil ls oss://ai-blog-backup/media/
```

---

## 检查清单

部署完成后，逐项检查：

### 基础部署
- [ ] GitHub 仓库已创建并推送代码
- [ ] 服务器已安装所有依赖
- [ ] MySQL 数据库已创建
- [ ] `.env` 文件已正确配置
- [ ] 数据库迁移已执行
- [ ] 静态文件已收集
- [ ] Gunicorn 服务正常运行
- [ ] Nginx 配置正确
- [ ] HTTP 访问正常
- [ ] SSL 证书已申请
- [ ] HTTPS 访问正常
- [ ] 管理后台 `/admin/` 可访问
- [ ] 媒体文件上传正常

### 数据安全
- [ ] OSS Bucket 已创建
- [ ] ossutil 已配置并可连接
- [ ] 备份脚本已创建
- [ ] Cron 定时任务已配置
- [ ] 备份测试成功
- [ ] 恢复流程已验证

### 安全加固
- [ ] SSH 端口已修改
- [ ] root 登录已禁用
- [ ] SSH Key 已配置
- [ ] 密码登录已禁用
- [ ] 防火墙只开放必要端口
- [ ] MySQL 安全配置完成
- [ ] `.env` 权限为 600
- [ ] Nginx 安全头已配置
- [ ] 自动安全更新已启用

---

## 联系与支持

如遇到问题，请检查：
1. 服务状态：`sudo systemctl status ai_blog nginx`
2. 日志文件：`sudo journalctl -u ai_blog -f`
3. Nginx 日志：`/var/log/nginx/error.log`
4. 备份日志：`/var/log/ai_blog_backup.log`
5. Cron 日志：`grep CRON /var/log/syslog`

---

## 附录

### A. 常用命令速查

| 功能 | 命令 |
|------|------|
| 重启 Gunicorn | `sudo systemctl restart ai_blog` |
| 重启 Nginx | `sudo systemctl restart nginx` |
| 查看服务状态 | `sudo systemctl status ai_blog nginx` |
| 查看日志 | `sudo journalctl -u ai_blog -f` |
| 手动备份 | `sudo /var/www/ai_blog/scripts/backup.sh` |
| 查看 OSS 备份 | `ossutil ls oss://ai-blog-backup/` |
| 检查防火墙 | `sudo ufw status` |
| 更新代码 | `git pull && pip install -r requirements.txt && python manage.py migrate` |

### B. 目录结构

```
/var/www/ai_blog/
├── venv/                    # Python 虚拟环境
├── config/                  # Django 配置
├── apps/                    # Django 应用
├── templates/               # 模板文件
├── static/                  # 静态源文件
├── staticfiles/             # 收集的静态文件
├── media/                   # 上传的媒体文件
│   ├── articles/images/     # 文章图片
│   ├── hero/blocks/         # Hero 页面图片
│   └── site/                # 网站图片
├── scripts/                 # 脚本文件
│   └── backup.sh            # 备份脚本
├── .env                     # 环境变量
├── manage.py
└── requirements.txt
```

### C. 端口说明

| 端口 | 服务 | 说明 |
|------|------|------|
| 22/2222 | SSH | 服务器远程连接 |
| 80 | Nginx | HTTP（重定向到 HTTPS） |
| 443 | Nginx | HTTPS |
| 8000 | Gunicorn | Django 应用（仅本地） |
| 3306 | MySQL | 数据库（仅本地） |
