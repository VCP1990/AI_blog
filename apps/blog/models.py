from django.db import models
from django.utils.text import slugify
from markdownx.models import MarkdownxField
from apps.categories.models import Category
from apps.tags.models import Tag


class Article(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('zh-hans', '简体中文'),
    ]
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('published', '已发布'),
    ]

    language = models.CharField('语言', max_length=10, choices=LANGUAGE_CHOICES, default='en')
    title = models.CharField('文章标题', max_length=200)
    slug = models.SlugField('URL别名', max_length=220, unique=True, blank=True)
    summary = models.TextField('文章摘要', max_length=300, blank=True)
    content = MarkdownxField('文章内容', help_text='支持 Markdown 语法，可拖拽上传图片')
    cover_image = models.ImageField('封面图片', upload_to='articles/covers/', blank=True, null=True)
    
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='articles',
        verbose_name='所属分类'
    )
    tags = models.ManyToManyField(
        Tag, 
        blank=True, 
        related_name='articles',
        verbose_name='标签'
    )
    
    status = models.CharField('发布状态', max_length=10, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField('是否推荐', default=False)
    allow_comment = models.BooleanField('允许评论', default=True)
    
    views = models.PositiveIntegerField('阅读量', default=0)
    likes = models.PositiveIntegerField('点赞数', default=0)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    published_at = models.DateTimeField('发布时间', null=True, blank=True)

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = '文章'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['language', 'status', '-published_at']),
            models.Index(fields=['slug']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f'[{self.get_language_display()}] {self.title}'

    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views'])

    def get_summary(self):
        if self.summary:
            return self.summary
        return self.content[:200] + '...' if len(self.content) > 200 else self.content
