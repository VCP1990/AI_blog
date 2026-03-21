from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('zh-hans', '简体中文'),
    ]
    
    language = models.CharField('语言', max_length=10, choices=LANGUAGE_CHOICES, default='en')
    name = models.CharField('分类名称', max_length=50)
    slug = models.SlugField('URL别名', max_length=60, unique=True, blank=True)
    description = models.TextField('分类描述', max_length=200, blank=True)
    order = models.PositiveIntegerField('排序', default=0)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = '分类'
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'[{self.get_language_display()}] {self.name}'

    def get_article_count(self):
        return self.articles.filter(status='published', language=self.language).count()
