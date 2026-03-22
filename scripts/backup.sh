#!/bin/bash
# AI Blog 备份脚本
# 用法: ./backup.sh [选项]
#   --db        仅备份数据库
#   --media     仅备份媒体文件
#   --all       备份全部（默认）

set -e

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 加载配置
source "$SCRIPT_DIR/config.sh"

# ========== 日志函数 ==========
log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ========== 参数默认值 ==========
BACKUP_DB=true
BACKUP_MEDIA=true

# ========== 参数解析 ==========
while [[ $# -gt 0 ]]; do
    case $1 in
        --db) BACKUP_MEDIA=false ;;
        --media) BACKUP_DB=false ;;
        --all) BACKUP_DB=true; BACKUP_MEDIA=true ;;
        *) log_error "未知参数: $1"; exit 1 ;;
    esac
    shift
done

# ========== 开始备份 ==========
echo ""
echo "=============================================="
echo "        AI Blog 数据备份"
echo "=============================================="
echo ""

BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR_LOCAL="./backups"

# 创建本地备份目录
mkdir -p "$BACKUP_DIR_LOCAL"

# ========== 1. 备份数据库 ==========
if [ "$BACKUP_DB" = true ]; then
    log_info "备份数据库..."
    
    DB_BACKUP_FILE="db_backup_$BACKUP_DATE.sql"
    
    # 在服务器上导出数据库
    ssh $SERVER "mysqldump -u $DB_USER -p'$DB_PASS' $DB_NAME > $DB_BACKUP_DIR/$DB_BACKUP_FILE 2>/dev/null"
    
    # 下载到本地
    scp $SERVER:$DB_BACKUP_DIR/$DB_BACKUP_FILE "$BACKUP_DIR_LOCAL/$DB_BACKUP_FILE"
    
    # 压缩
    gzip "$BACKUP_DIR_LOCAL/$DB_BACKUP_FILE"
    
    # 删除服务器上的临时文件
    ssh $SERVER "rm -f $DB_BACKUP_DIR/$DB_BACKUP_FILE"
    
    log_info "数据库备份完成: $BACKUP_DIR_LOCAL/${DB_BACKUP_FILE}.gz"
fi

# ========== 2. 备份媒体文件 ==========
if [ "$BACKUP_MEDIA" = true ]; then
    log_info "备份媒体文件..."
    
    MEDIA_BACKUP_FILE="media_backup_$BACKUP_DATE.tar.gz"
    
    # 在服务器上打包
    ssh $SERVER "cd $PROJECT_DIR && tar -czf $DB_BACKUP_DIR/$MEDIA_BACKUP_FILE media/"
    
    # 下载到本地
    scp $SERVER:$DB_BACKUP_DIR/$MEDIA_BACKUP_FILE "$BACKUP_DIR_LOCAL/$MEDIA_BACKUP_FILE"
    
    # 删除服务器上的临时文件
    ssh $SERVER "rm -f $DB_BACKUP_DIR/$MEDIA_BACKUP_FILE"
    
    log_info "媒体文件备份完成: $BACKUP_DIR_LOCAL/$MEDIA_BACKUP_FILE"
fi

# ========== 备份完成 ==========
echo ""
echo "=============================================="
log_info "备份完成！"
echo "=============================================="
echo ""
echo "备份目录: $BACKUP_DIR_LOCAL"
ls -lh "$BACKUP_DIR_LOCAL" | tail -5
echo ""
