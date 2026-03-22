#!/bin/bash
# AI Blog 回滚脚本
# 用法: ./rollback.sh [commit_hash]

set -e

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 加载配置
source "$SCRIPT_DIR/config.sh"

# ========== 日志函数 ==========
log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step()  { echo -e "${BLUE}[STEP]${NC} $1"; }

# ========== 参数检查 ==========
ROLLBACK_COMMIT=${1:-}

if [ -z "$ROLLBACK_COMMIT" ]; then
    # 获取上一个 commit
    ROLLBACK_COMMIT=$(ssh $SERVER "cd $PROJECT_DIR && git rev-parse HEAD~1" 2>/dev/null)
    if [ -z "$ROLLBACK_COMMIT" ]; then
        log_error "无法获取上一个 commit"
        exit 1
    fi
    log_info "将回滚到上一个 commit: $ROLLBACK_COMMIT"
else
    log_info "将回滚到指定 commit: $ROLLBACK_COMMIT"
fi

# 确认回滚
read -p "确认回滚？(y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "回滚已取消"
    exit 0
fi

echo ""
echo "=============================================="
echo "        AI Blog 回滚操作"
echo "=============================================="
echo ""

# ========== 1. 开启维护模式 ==========
log_step "1/5 开启维护模式"
ssh $SERVER "touch $MAINTENANCE_FILE && nginx -s reload"
log_info "维护模式已开启"

# ========== 2. 回滚代码 ==========
log_step "2/5 回滚代码"
CURRENT_COMMIT=$(ssh $SERVER "cd $PROJECT_DIR && git rev-parse --short HEAD")
ssh $SERVER "cd $PROJECT_DIR && git reset --hard $ROLLBACK_COMMIT"
NEW_COMMIT=$(ssh $SERVER "cd $PROJECT_DIR && git rev-parse --short HEAD")
log_info "代码已回滚: $CURRENT_COMMIT → $NEW_COMMIT"

# ========== 3. 更新依赖 ==========
log_step "3/5 更新依赖"
ssh $SERVER "cd $PROJECT_DIR && source $VENV_ACTIVATE && pip install -r requirements.txt"
log_info "依赖已更新"

# ========== 4. 重启服务 ==========
log_step "4/5 重启服务"
ssh $SERVER "systemctl restart $SERVICE_NAME"
sleep 3

SERVICE_STATUS=$(ssh $SERVER "systemctl is-active $SERVICE_NAME")
if [ "$SERVICE_STATUS" = "active" ]; then
    log_info "服务重启成功"
else
    log_error "服务启动失败！"
    exit 1
fi

# ========== 5. 关闭维护模式 ==========
log_step "5/5 关闭维护模式"
ssh $SERVER "rm -f $MAINTENANCE_FILE && nginx -s reload"
log_info "维护模式已关闭"

# ========== 回滚完成 ==========
echo ""
echo "=============================================="
log_info "回滚完成！"
echo "=============================================="
echo ""
echo "版本: $CURRENT_COMMIT → $NEW_COMMIT"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
