from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import SiteSettings, Announcement, HeroPage, HeroContentBlock, HeroCTA


class HeroContentBlockInline(admin.TabularInline):
    model = HeroContentBlock
    extra = 1
    fields = ('title', 'content', 'image', 'image_position', 'order', 'is_active')
    ordering = ['order']


class HeroCTAInline(admin.StackedInline):
    model = HeroCTA
    extra = 0
    max_num = 1
    fields = ('background_image', 'content', 'button_text', 'link_type', 'internal_link', 'external_url', 'is_active')


@admin.register(HeroPage)
class HeroPageAdmin(MarkdownxModelAdmin):
    list_display = ['title', 'language', 'is_active', 'content_blocks_count', 'has_cta', 'updated_at']
    list_filter = ['is_active', 'language', 'created_at']
    search_fields = ['title', 'subtitle']
    inlines = [HeroContentBlockInline, HeroCTAInline]
    fieldsets = (
        ('板块一：标题区域', {
            'fields': ('title', 'subtitle', 'welcome_text', 'background_image')
        }),
        ('语言', {
            'fields': ('language',)
        }),
        ('状态', {
            'fields': ('is_active',)
        }),
    )

    def content_blocks_count(self, obj):
        return obj.content_blocks.filter(is_active=True).count()
    content_blocks_count.short_description = '内容块数量'

    def has_cta(self, obj):
        return obj.cta.is_active if hasattr(obj, 'cta') else False
    has_cta.boolean = True
    has_cta.short_description = 'CTA'


@admin.register(HeroContentBlock)
class HeroContentBlockAdmin(MarkdownxModelAdmin):
    list_display = ['title', 'hero_page', 'image_preview', 'image_position', 'order', 'is_active']
    list_filter = ['hero_page', 'is_active', 'image_position']
    search_fields = ['title', 'content']
    list_editable = ['order', 'is_active']
    ordering = ['hero_page', 'order']

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="max-height: 50px; max-width: 100px; border-radius: 4px;">'
        return '-'
    image_preview.allow_tags = True
    image_preview.short_description = '图片预览'


@admin.register(HeroCTA)
class HeroCTAAdmin(MarkdownxModelAdmin):
    list_display = ['hero_page', 'button_text', 'link_type', 'get_link_display', 'is_active']
    list_filter = ['link_type', 'is_active']
    list_editable = ['is_active']

    def get_link_display(self, obj):
        return obj.get_link() or '-'
    get_link_display.short_description = '链接'


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'language', 'author_name', 'updated_at']
    list_filter = ['language']
    
    fieldsets = (
        ('网站基本信息', {
            'fields': ('site_name', 'site_description')
        }),
        ('语言', {
            'fields': ('language',)
        }),
        ('博客页面', {
            'fields': ('blog_title', 'blog_subtitle')
        }),
        ('作者信息', {
            'fields': ('author_name', 'author_title', 'author_avatar', 'author_bio')
        }),
        ('我的服务', {
            'fields': ('services_content',)
        }),
        ('联系方式', {
            'fields': ('contact_email', 'contact_github', 'contact_linkedin', 'contact_twitter')
        }),
        ('页脚', {
            'fields': ('footer_text',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['language']
        return []
    
    def has_add_permission(self, request):
        existing_languages = set(SiteSettings.objects.values_list('language', flat=True))
        allowed_languages = set(dict(SiteSettings.LANGUAGE_CHOICES).keys())
        return bool(allowed_languages - existing_languages)
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:
            existing_languages = set(SiteSettings.objects.values_list('language', flat=True))
            available_languages = [(k, v) for k, v in SiteSettings.LANGUAGE_CHOICES if k not in existing_languages]
            form.base_fields['language'].choices = available_languages
        return form


@admin.register(Announcement)
class AnnouncementAdmin(MarkdownxModelAdmin):
    list_display = ['content_preview', 'language', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'language', 'created_at']
    list_editable = ['is_active']
    search_fields = ['content']
    ordering = ['-created_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '公告内容'
