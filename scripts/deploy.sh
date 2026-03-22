#!/bin/bash
# AI Blog 自动化部署脚本
# 用法: ./deploy.sh [选项]
#   --backup          部署前备份数据库
#   --skip-migration  跳过数据库迁移
#   --dry-run         模拟运行（不执行实际操作）
#   --quick           快速部署（跳过备份和迁移检查）

set -e  # 遇错即停

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 加载配置
source "$SCRIPT_DIR/config.sh"

# ========== 参数默认值 ==========
BACKUP=false
SKIP_MIGRATION=false
DRY_RUN=false
QUICK=false

# ========== 日志函数 ==========
log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step()  { echo -e "${BLUE}[STEP]${NC} $1"; }

# ========== 远程执行函数 ==========
remote_exec() {
    if [ "$DRY_RUN" = true ]; then
        echo "[DRY-RUN] ssh $SERVER \"$1\""
    else
        ssh $SERVER "$1"
    fi
}

# ========== 参数解析 ==========
while [[ $# -gt 0 ]]; do
    case $1 in
        --backup) BACKUP=true ;;
        --skip-migration) SKIP_MIGRATION=true ;;
        --dry-run) DRY_RUN=true ;;
        --quick) QUICK=true ;;
        -h|--help)
            echo "用法: $0 [选项]"
            echo "选项:"
            echo "  --backup          部署前备份数据库"
            echo "  --skip-migration  跳过数据库迁移"
            echo "  --dry-run         模拟运行"
            echo "  --quick           快速部署（仅更新代码和重启）"
            exit 0
            ;;
        *) log_error "未知参数: $1"; exit 1 ;;
    esac
    shift
done

# ========== 开始部署 ==========
echo ""
echo "=============================================="
echo "        AI Blog 自动化部署"
echo "=============================================="
echo ""

# 记录开始时间
START_TIME=$(date +%s)

# ========== 1. 前置检查 ==========
log_step "1/10 前置检查"

# 检查本地是否有未提交的更改
if [ "$DRY_RUN" = false ]; then
    if ! git diff-index --quiet HEAD --; then
        log_warn "本地有未提交的更改"
        read -p "是否继续部署？(y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "部署已取消"
            exit 0
        fi
    fi
fi

# 检查服务器连接
log_info "检查服务器连接..."
if ! remote_exec "echo '连接成功'" > /dev/null 2>&1; then
    log_error "无法连接到服务器"
    exit 1
fi

# 获取当前服务器版本
CURRENT_COMMIT=$(remote_exec "cd $PROJECT_DIR && git rev-parse --short HEAD" 2>/dev/null || echo "unknown")
log_info "当前服务器版本: $CURRENT_COMMIT"

# ========== 2. 开启维护模式 ==========
log_step "2/10 开启维护模式"
remote_exec "touch $MAINTENANCE_FILE"
remote_exec "nginx -s reload"
log_info "维护模式已开启"

# ========== 3. 备份数据库 ==========
if [ "$BACKUP" = true ] && [ "$QUICK" = false ]; then
    log_step "3/10 备份数据库"
    BACKUP_FILE="db_backup_$(date +%Y%m%d_%H%M%S).sql"
    remote_exec "mysqldump -u$DB_USER -p'$DB_PASS' $DB_NAME > $DB_BACKUP_DIR/$BACKUP_FILE"
    if [ $? -eq 0 ]; then
        log_info "数据库已备份: $BACKUP_FILE"
    else
        log_error "数据库备份失败"
    fi
else
    log_step "3/10 跳过数据库备份"
fi

# ========== 4. 拉取代码 ==========
log_step "4/10 拉取最新代码"
remote_exec "cd $PROJECT_DIR && git fetch origin"
remote_exec "cd $PROJECT_DIR && git pull origin main"
NEW_COMMIT=$(remote_exec "cd $PROJECT_DIR && git rev-parse --short HEAD")
log_info "更新到版本: $NEW_COMMIT"

# ========== 5. 更新依赖 ==========
log_step "5/10 检查依赖更新"
remote_exec "cd $PROJECT_DIR && source $VENV_ACTIVATE && pip install -r requirements.txt --quiet"
log_info "依赖已更新"

# ========== 6. 数据库迁移 ==========
if [ "$SKIP_MIGRATION" = true ] || [ "$QUICK" = true ]; then
    log_step "6/10 跳过数据库迁移"
else
    log_step "6/10 执行数据库迁移"
    remote_exec "cd $PROJECT_DIR && source $VENV_ACTIVATE && DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS python manage.py migrate --noinput"
    log_info "数据库迁移完成"
fi

# ========== 7. 收集静态文件 ==========
log_step "7/10 收集静态文件"
remote_exec "cd $PROJECT_DIR && source $VENV_ACTIVATE && DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS python manage.py collectstatic --noinput"
log_info "静态文件已收集"

# ========== 8. 重启服务 ==========
log_step "8/10 重启服务"
remote_exec "systemctl restart $SERVICE_NAME"
sleep 3

# 检查服务状态
SERVICE_STATUS=$(remote_exec "systemctl is-active $SERVICE_NAME")
if [ "$SERVICE_STATUS" = "active" ]; then
    log_info "服务重启成功"
else
    log_error "服务启动失败！"
    log_info "查看日志: ssh $SERVER 'journalctl -u $SERVICE_NAME -n 50'"
    exit 1
fi

# ========== 9. 健康检查 ==========
log_step "9/10 健康检查"
sleep 2
HTTP_STATUS=$(remote_exec "curl -s -o /dev/null -w '%{http_code}' https://paoresearch.top/en/")
if [ "$HTTP_STATUS" = "200" ]; then
    log_info "网站响应正常 (HTTP $HTTP_STATUS)"
else
    log_warn "网站响应异常 (HTTP $HTTP_STATUS)"
fi

# ========== 10. 关闭维护模式 ==========
log_step "10/10 关闭维护模式"
remote_exec "rm -f $MAINTENANCE_FILE"
remote_exec "nginx -s reload"
log_info "维护模式已关闭"

# ========== 部署完成 ==========
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo "=============================================="
log_info "部署完成！"
echo "=============================================="
echo ""
echo "版本: $CURRENT_COMMIT → $NEW_COMMIT"
echo "耗时: ${DURATION}秒"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
