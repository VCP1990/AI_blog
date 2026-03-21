from django.contrib import admin
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'language', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'language']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']

    
    def get_article_count(self, obj):
        return obj.articles.filter(status='published', language=obj.language).count()
    get_article_count.short_description = '文章数量'
