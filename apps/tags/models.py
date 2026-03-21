from django.db import models
from django.utils.text import slugify


class Tag(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('zh-hans', '简体中文'),
    ]
    
    language = models.CharField('语言', max_length=10, choices=LANGUAGE_CHOICES, default='en')
    name = models.CharField('标签名称', max_length=30)
    slug = models.SlugField('URL别名', max_length=40, unique=True, blank=True)
    color = models.CharField('标签颜色', max_length=7, default='#3b82f6', help_text='HEX颜色值，如 #3b82f6')
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = '标签'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'[{self.get_language_display()}] {self.name}'

    def get_article_count(self):
        return self.articles.filter(status='published', language=self.language).count()
