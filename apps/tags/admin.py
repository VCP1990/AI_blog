from django.contrib import admin
from .models import Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'language', 'slug', 'color', 'is_active', 'get_article_count', 'created_at']
    list_filter = ['is_active', 'language']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']
    
    def get_article_count(self, obj):
        return obj.articles.filter(status='published', language=obj.language).count()
    get_article_count.short_description = '文章数量'
