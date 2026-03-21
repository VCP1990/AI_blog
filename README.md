# AI Blog

A modern personal blog system built with Django 5.x, featuring a dark theme design, bilingual support, and responsive layout.

## Features

- **Hero Homepage** - AI consulting landing page with backend configuration (title, content blocks, CTA)
- **Bilingual Support** - English (`/en/`) and Simplified Chinese (`/zh-hans/`) with language switcher
- **Landing Page** - Personal bio, services, and contact information
- **Blog System** - Complete management of articles, categories, and tags
- **Blog Welcome Message** - Customizable blog page title and subtitle (backend config)
- **Announcement System** - Top banner on blog page, supports Markdown, dismissible
- **Markdown Editor** - Markdown syntax with live preview, drag-drop image upload
- **Code Highlighting** - GitHub Dark style syntax highlighting, auto-generated TOC
- **Internal Links** - Use `@[article title]` to reference other articles
- **About Page** - "About Me" and "My Services" support Markdown editing with image upload
- **Full-text Search** - Search by title, content, or summary
- **RSS Feed** - Article RSS subscription
- **Responsive Design** - Perfect adaptation for desktop and mobile
- **Dark Theme** - Eye-friendly dark interface

## Tech Stack

| Category | Technology |
|----------|------------|
| Backend Framework | Django 5.x |
| Frontend Interaction | htmx |
| Frontend Styles | Tailwind CSS 3.x (CDN) |
| Markdown Editor | django-markdownx |
| Code Highlighting | highlight.js (GitHub Dark) |
| Icons | Lucide Icons |
| Database | SQLite (dev) / MySQL (production) |
| WSGI | Gunicorn |
| Reverse Proxy | Nginx |
| Media Storage | Aliyun OSS (optional) |

## Project Structure

```
AI_blog/
├── config/                    # Django project configuration
│   ├── settings/
│   │   ├── base.py           # Base settings
│   │   ├── development.py    # Development environment
│   │   └── production.py     # Production environment
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── core/                 # Core features (home/search/RSS/HeroPage)
│   ├── blog/                 # Blog articles
│   ├── categories/           # Category management
│   └── tags/                 # Tag management
├── templates/
│   ├── base.html
│   ├── hero/
│   │   ├── index.html            # Hero homepage (static fallback)
│   │   └── index_dynamic.html    # Hero homepage (dynamic template)
│   ├── landing/
│   │   └── about.html
│   ├── blog/
│   └── partials/
├── static/                    # Static files
├── media/                     # Uploaded files
├── locale/                    # Translation files
│   ├── en/LC_MESSAGES/
│   └── zh_Hans/LC_MESSAGES/
├── manage.py
├── requirements.txt
├── gunicorn.conf.py
├── nginx.conf.example
├── .env.example
└── README.md
```

## Requirements

- Python 3.10+
- MySQL 8.0+ (production)
- Nginx (production)

## Quick Start

### 1. Install Dependencies

```bash
python -m venv .venv

.venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` file with your settings.

### 3. Initialize Database

```bash
set DJANGO_SETTINGS_MODULE=config.settings.development

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 4. Run Development Server

```bash
python manage.py runserver
```

Access:
- Homepage: http://127.0.0.1:8000 (redirects to /en/)
- English: http://127.0.0.1:8000/en/
- Chinese: http://127.0.0.1:8000/zh-hans/
- Blog: http://127.0.0.1:8000/en/blog/
- Admin: http://127.0.0.1:8000/admin/

## Backend Configuration

### Site Settings

After logging into admin, configure in **Site Settings**:

- Site name, description
- Blog title, subtitle
- Author info (name, title, bio, avatar)
- My Services (Markdown editing, supports image upload)
- Contact info (email, GitHub, LinkedIn, Twitter)

### Hero Page Configuration

Configure homepage content in **Hero Pages**:

1. **Section 1: Title Area**
   - Main title
   - Subtitle
   - Welcome text (supports Markdown)

2. **Section 2: Content Blocks** (supports multiple, sortable)
   - Block title
   - Content (supports Markdown)
   - Image upload
   - Image position (left/right/center/none)

3. **Section 3: CTA**
   - CTA content (supports Markdown)
   - Button text
   - Link type (internal link/external URL)
   - Internal link examples: `/about/`, `/blog/`

**Note**: Only one HeroPage can be active at a time. Activating a new one automatically deactivates others.

### Content Management

1. **Categories** - Create article categories
2. **Tags** - Create tags and set colors
3. **Articles** - Publish blog articles

### Markdown Editor

Backend article editing supports **Markdown syntax** with:

- **Live Preview** - Right side of editor shows rendered output
- **Image Upload** - Drag or paste images, auto-upload to server
- **Code Highlighting** - Multiple programming language syntax highlighting
- **Table Support** - Markdown table syntax

**Supported Markdown syntax:**

```markdown
# Heading 1
## Heading 2
### Heading 3

**Bold** *Italic* `code`

- Unordered list
1. Ordered list

> Blockquote

[Link](https://example.com)
![Image](path/to/image.png)

| Header 1 | Header 2 |
|----------|----------|
| Content 1| Content 2|

```python
def hello():
    print("Hello, World!")
```
```

## URL Routes

| Page | URL | Description |
|------|-----|-------------|
| Hero Homepage | `/en/` or `/zh-hans/` | AI consulting landing page (backend configurable) |
| Landing | `/en/about/` | Personal introduction page |
| Blog List | `/en/blog/` | All articles list |
| Article Detail | `/en/blog/<slug>/` | Single article page |
| Category Articles | `/en/blog/category/<slug>/` | Articles by category |
| Tag Articles | `/en/blog/tag/<slug>/` | Articles by tag |
| Search | `/en/search/?q=keyword` | Search results page |
| RSS | `/en/rss/` | RSS feed |
| Admin | `/admin/` | Admin backend |

**Note**: Replace `/en/` with `/zh-hans/` for Chinese version.

## Production Deployment

### Recommended: Aliyun (Alibaba Cloud)

This project is optimized for Aliyun deployment:

- **ECS / Light Application Server** - Native Django support
- **RDS MySQL** - Direct MySQL compatibility
- **OSS** - Media file storage (configured in `.env`)
- **CDN** - Static file acceleration

### 1. Server Environment (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx mysql-server

sudo apt install libmysqlclient-dev
```

### 2. Project Deployment

```bash
sudo mkdir -p /var/www/ai_blog
sudo chown $USER:$USER /var/www/ai_blog

cd /var/www/ai_blog

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 3. Configure Gunicorn

Create `/etc/systemd/system/ai_blog.service`:

```ini
[Unit]
Description=AI Blog Gunicorn
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/ai_blog
Environment="PATH=/var/www/ai_blog/.venv/bin"
Environment="DJANGO_ENVIRONMENT=production"
ExecStart=/var/www/ai_blog/.venv/bin/gunicorn --config gunicorn.conf.py config.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

Start service:

```bash
sudo systemctl daemon-reload
sudo systemctl start ai_blog
sudo systemctl enable ai_blog
```

### 4. Configure Nginx

```bash
sudo cp nginx.conf.example /etc/nginx/sites-available/ai_blog
sudo ln -s /etc/nginx/sites-available/ai_blog /etc/nginx/sites-enabled/
```

Modify domain and SSL certificate path in config, then:

```bash
sudo nginx -t
sudo systemctl restart nginx
```

### 5. SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| DJANGO_ENVIRONMENT | Runtime environment | development / production |
| DJANGO_SECRET_KEY | Secret key | random string |
| DJANGO_ALLOWED_HOSTS | Allowed domains | example.com,www.example.com |
| DB_NAME | Database name | ai_blog |
| DB_USER | Database user | root |
| DB_PASSWORD | Database password | your-password |
| DB_HOST | Database host | localhost |
| DB_PORT | Database port | 3306 |
| EMAIL_HOST | SMTP server | smtp.qq.com |
| EMAIL_PORT | SMTP port | 587 |
| EMAIL_HOST_USER | Email address | your-email@qq.com |
| EMAIL_HOST_PASSWORD | Email password | your-password |
| OSS_ACCESS_KEY_ID | Aliyun OSS Access Key | (optional) |
| OSS_ACCESS_KEY_SECRET | Aliyun OSS Secret | (optional) |
| OSS_BUCKET_NAME | OSS bucket name | (optional) |
| OSS_ENDPOINT | OSS endpoint | oss-cn-hangzhou.aliyuncs.com |

## Design Specs

### Color Scheme

| Usage | Color Value |
|-------|-------------|
| Background | `#0f172a` |
| Card Background | `#1e293b` |
| Border | `#334155` |
| Text | `#f1f5f9` |
| Secondary Text | `#94a3b8` |
| Accent | `#3b82f6` |

### Layout

- Two-column layout: Content 66% + Sidebar 33%
- Max width: 1280px
- Responsive breakpoints: md (768px), lg (1024px)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

MIT License
