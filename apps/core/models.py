from django.db import models
from markdownx.models import MarkdownxField


class SiteSettings(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('zh-hans', '简体中文'),
    ]
    
    language = models.CharField('语言', max_length=10, choices=LANGUAGE_CHOICES, default='en')
    site_name = models.CharField('网站名称', max_length=100, default='AI Blog')
    site_description = models.TextField('网站描述', max_length=300, blank=True)
    
    blog_title = models.CharField('博客标题', max_length=100, default='Blog')
    blog_subtitle = models.CharField('博客副标题', max_length=200, default='Exploring thoughts on technology', help_text='支持 @[文章标题] 引用内部文章链接')
    
    author_name = models.CharField('作者姓名', max_length=50, default='Your Name')
    author_title = models.CharField('作者头衔', max_length=100, default='Full Stack Developer')
    author_avatar = models.ImageField('作者头像', upload_to='site/', blank=True, null=True)
    author_bio = MarkdownxField('作者简介', help_text='支持 Markdown 语法，可使用 @[文章标题] 引用内部文章', blank=True)
    
    services_content = MarkdownxField('我的服务', help_text='支持 Markdown 语法和图片上传，可使用 @[文章标题] 引用内部文章', blank=True)
    
    contact_email = models.EmailField('联系邮箱', blank=True)
    contact_github = models.URLField('GitHub', blank=True)
    contact_linkedin = models.URLField('LinkedIn', blank=True)
    contact_twitter = models.URLField('Twitter/X', blank=True)
    
    footer_text = models.CharField('页脚文字', max_length=200, default='© 2026 AI Blog. All rights reserved.')
    
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '网站设置'
        verbose_name_plural = '网站设置'
        constraints = [
            models.UniqueConstraint(fields=['language'], name='unique_site_settings_per_language')
        ]

    def __str__(self):
        return f'{self.site_name} ({self.get_language_display()})'

    @classmethod
    def get_settings(cls, language='en'):
        settings = cls.objects.filter(language=language).first()
        if not settings:
            settings, _ = cls.objects.get_or_create(
                language=language,
                defaults={'site_name': 'AI Blog'}
            )
        return settings


class Announcement(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('zh-hans', '简体中文'),
    ]
    
    language = models.CharField('语言', max_length=10, choices=LANGUAGE_CHOICES, default='en')
    content = MarkdownxField('公告内容', help_text='支持 Markdown 语法，可使用 @[文章标题] 引用内部文章')
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '公告'
        verbose_name_plural = '公告'
        ordering = ['-created_at']

    def __str__(self):
        return self.content[:50] + '...' if len(self.content) > 50 else self.content


class HeroPage(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('zh-hans', '简体中文'),
    ]
    
    language = models.CharField('语言', max_length=10, choices=LANGUAGE_CHOICES, default='en')
    title = models.CharField('主标题', max_length=200)
    subtitle = models.CharField('副标题', max_length=300, blank=True)
    welcome_text = MarkdownxField('欢迎词', help_text='支持 Markdown 语法')
    background_image = models.ImageField('背景图', upload_to='hero/backgrounds/', blank=True, null=True)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = 'Hero页面'
        verbose_name_plural = 'Hero页面'
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.title} ({self.get_language_display()})'

    def save(self, *args, **kwargs):
        if self.is_active:
            HeroPage.objects.filter(is_active=True, language=self.language).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_active(cls, language='en'):
        return cls.objects.filter(is_active=True, language=language).first()


class HeroContentBlock(models.Model):
    IMAGE_POSITION_CHOICES = [
        ('left', '左侧'),
        ('right', '右侧'),
        ('center', '居中'),
        ('none', '不显示图片'),
    ]

    hero_page = models.ForeignKey(HeroPage, on_delete=models.CASCADE, related_name='content_blocks', verbose_name='所属页面')
    title = models.CharField('块标题', max_length=200, blank=True)
    content = MarkdownxField('内容', help_text='支持 Markdown 语法')
    image = models.ImageField('图片', upload_to='hero/blocks/', blank=True, null=True)
    image_position = models.CharField('图片位置', max_length=10, choices=IMAGE_POSITION_CHOICES, default='right')
    order = models.PositiveIntegerField('排序', default=0, help_text='数字越小越靠前')
    is_active = models.BooleanField('是否显示', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '内容块'
        verbose_name_plural = '内容块'
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.title or f'内容块 #{self.order}'


class HeroCTA(models.Model):
    LINK_TYPE_CHOICES = [
        ('internal', '内部链接'),
        ('external', '外部链接'),
    ]

    hero_page = models.OneToOneField(HeroPage, on_delete=models.CASCADE, related_name='cta', verbose_name='所属页面')
    background_image = models.ImageField('背景图', upload_to='hero/cta/', blank=True, null=True)
    content = MarkdownxField('CTA内容', help_text='支持 Markdown 语法')
    button_text = models.CharField('按钮文字', max_length=100, default='了解更多')
    link_type = models.CharField('链接类型', max_length=10, choices=LINK_TYPE_CHOICES, default='internal')
    internal_link = models.CharField('内部链接', max_length=200, blank=True, help_text='如: /about/, /blog/')
    external_url = models.URLField('外部URL', blank=True)
    is_active = models.BooleanField('是否显示', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = 'CTA'
        verbose_name_plural = 'CTA'

    def __str__(self):
        return f'{self.hero_page.title} - CTA'

    def get_link(self):
        if self.link_type == 'internal':
            return self.internal_link
        return self.external_url
