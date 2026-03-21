from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import Article


@admin.register(Article)
class ArticleAdmin(MarkdownxModelAdmin):
    list_display = ['title', 'language', 'category', 'status', 'is_featured', 'views', 'created_at', 'published_at']
    list_filter = ['status', 'language', 'is_featured', 'category', 'tags']
    search_fields = ['title', 'content', 'summary']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    readonly_fields = ['views', 'likes', 'created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'slug', 'language', 'summary', 'content', 'cover_image')
        }),
        ('分类与标签', {
            'fields': ('category', 'tags')
        }),
        ('发布设置', {
            'fields': ('status', 'is_featured', 'allow_comment', 'published_at')
        }),
        ('统计信息', {
            'fields': ('views', 'likes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if obj.status == 'published' and not obj.published_at:
            from django.utils import timezone
            obj.published_at = timezone.now()
        super().save_model(request, obj, form, change)
