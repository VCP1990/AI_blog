# AI Blog Changelog

All changes and updates are recorded in this file.
---

## [2026-03-16] - v1.8.0

### Fixed
- **i18n Language Code** - Changed from `zh` to `zh-hans` for Django 5.x compatibility
  - Django 5.x only supports `zh-hans` (Simplified Chinese) and `zh-hant` (Traditional Chinese)
  - Updated `LANGUAGES` in `config/settings/base.py`
  - Updated all model `LANGUAGE_CHOICES` fields
  - Renamed `locale/zh/` to `locale/zh_Hans/`
  - Updated `get_current_language()` in views to detect `zh-hans`

- **URL Routing** - Fixed language prefix behavior
  - Changed `prefix_default_language=True` so all languages require prefix
  - `/` redirects to `/en/`
  - `/en/` for English, `/zh-hans/` for Chinese

### Modified
- **Hero Page Navigation** - Added navbar to both hero page templates
  - `templates/hero/index.html` - Added navbar include, Tailwind CDN, Lucide Icons
  - `templates/hero/index_dynamic.html` - Same updates
  - Added `pt-20` padding to content area for fixed navbar

- **UI Text Internationalization** - Changed all hardcoded Chinese text to English
  - `partials/sidebar.html`: Categories, Tags, Popular Articles, Subscribe, etc.
  - `landing/about.html`: About Me, My Services, Contact Me, etc.
  - `blog/*.html`: Date format, search text, empty states, etc.
  - `hero/*.html`: Footer links (About, Blog)

### Database Migration
- Migration files:
  - `blog.0004_alter_article_language`
  - `categories.0003_alter_category_language`
  - `core.0006_alter_announcement_language_alter_heropage_language_and_more`
  - `tags.0003_alter_tag_language`
- Changed `language` field `max_length` from 2 to 10

---

## [2026-03-16] - v1.7.0

### Added
- **Bilingual Support (EN/ZH)** - Independent language versions, content not translated
  - URL language prefix: `/en/` (English, default), `/zh/` (Chinese)
  - Navbar language switcher dropdown
  - Added `language` field to all models (Article, Category, Tag, HeroPage, SiteSettings, Announcement)
  - Views automatically filter content by current language

### Modified
- **Django i18n Configuration** (`config/settings/base.py`)
  - Added `LANGUAGES`, `LANGUAGE_CODE`, `LOCALE_PATHS`
  - Added `LocaleMiddleware`
  
- **URL Configuration** (`config/urls.py`)
  - Used `i18n_patterns` for language-prefixed routes
  - Added language switch URL `/set-language/<lang_code>/`

- **Model Changes**
  - `Article`: Added `language` field
  - `Category`: Added `language` field
  - `Tag`: Added `language` field
  - `HeroPage`: Added `language` field, modified `get_active()` to support language parameter
  - `SiteSettings`: Added `language` field, modified `get_settings()` to support language parameter
  - `Announcement`: Added `language` field

- **View Changes** (`apps/core/views.py`)
  - Added `get_current_language()` helper function
  - Added language filtering logic to all view functions

- **Template Changes**
  - `base.html`: Added i18n template tags
  - `navbar.html`: Added language switcher dropdown

- **Translation Files**
  - Added `locale/en/LC_MESSAGES/django.po`
  - Added `locale/zh/LC_MESSAGES/django.po`

### Database Migration
- Migration files:
  - `blog.0003_add_language_field`
  - `categories.0002_add_language_field`
  - `tags.0002_add_language_field`
  - `core.0005_add_language_field`

---

## [2026-03-16] - v1.6.0

### Added
- **Hero Page Dynamic Editing System** - Backend configurable homepage content
  - `HeroPage` model: Main page config (title, subtitle, welcome text)
  - `HeroContentBlock` model: Content blocks (Markdown + image upload support)
  - `HeroCTA` model: CTA config (content + internal/external link button)
  - Support multiple HeroPage versions, switch via `is_active`
  - Original hardcoded `hero/index.html` kept as fallback

### Admin Configuration
- `HeroPageAdmin`: Inline management of content blocks and CTA
- `HeroContentBlockAdmin`: Image preview, sort editing, position selection (left/right/center)
- `HeroCTAAdmin`: Link type toggle (internal link/external URL)

### Templates
- Added `templates/hero/index_dynamic.html`
  - Dark gradient style
  - Three image layouts: left/right/center
  - Markdown rendering support
  - Auto fallback: shows original when no active page

### View Logic
- `apps/core/views.py` `home()` function
  - Prioritizes loading `is_active=True` HeroPage
  - Falls back to original template when no active page

### Database Migration
- Migration file: `core.0004_add_hero_models`

---

## [2026-03-16] - v1.5.0

### Added
- **"My Services" Markdown Editor**
  - Changed fixed 3 service cards to single MarkdownxField (`services_content`)
  - Supports Markdown syntax editing
  - Supports image upload (via django-markdownx)
  - Supports `@[article title]` internal article link references
  - About page uses `.markdown-body` style rendering

### Modified
- **SiteSettings Model** (`apps/core/models.py`)
  - Removed `service_1_title`, `service_1_desc`, `service_1_icon`
  - Removed `service_2_title`, `service_2_desc`, `service_2_icon`
  - Removed `service_3_title`, `service_3_desc`, `service_3_icon`
  - Removed `hero_title`, `hero_subtitle`, `hero_background` (unused by Hero Page)
  - Added `services_content` (MarkdownxField)
  - Changed `author_bio` to MarkdownxField

- **Admin Configuration** (`apps/core/admin.py`)
  - Removed "Hero Area" fieldset
  - Removed "Services" fieldset (9 fixed fields)
  - Added "My Services" fieldset (single Markdown editor)

- **About Page Template** (`templates/landing/about.html`)
  - Removed 3 service card layout
  - Added Markdown content rendering area
  - Added `.markdown-body` style
  - Supports `article_link` and `markdown` filters

### Database Migration
- Migration file: `core.0003_remove_sitesettings_hero_background_and_more`
- Old data: `service_1/2/3_*` field data will be lost, please backup manually before migration

---

## [2026-03-16] - v1.4.0

### Added
- **Blog Welcome Message** - Customizable blog page title and subtitle
  - Added `blog_title` and `blog_subtitle` fields to SiteSettings
  - Blog list page displays custom title/subtitle

---

## [2026-03-14] - v1.0.0

### Initial Release
- Complete Django blog system
- Hero landing page
- Blog with categories and tags
- Markdown editor support
- Dark theme design
- Responsive layout
