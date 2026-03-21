import re
import markdown
from django import template
from django.utils.safestring import mark_safe
from apps.blog.models import Article

register = template.Library()


@register.filter(name='markdown')
def markdown_filter(text):
    """
    将 Markdown 文本转换为 HTML
    支持代码高亮、表格、TOC 等扩展
    """
    if not text:
        return ''
    
    md = markdown.Markdown(
        extensions=[
            'fenced_code',
            'codehilite',
            'tables',
            'toc',
            'nl2br',
            'sane_lists',
        ],
        extension_configs={
            'codehilite': {
                'css_class': 'highlight',
                'linenums': False,
                'guess_lang': True,
            },
            'toc': {
                'permalink': False,
                'toc_depth': 3,
                'title': '',
            }
        }
    )
    
    html = md.convert(text)
    return mark_safe(html)


@register.filter(name='markdown_toc')
def markdown_toc_filter(text):
    """
    从 Markdown 文本中提取 TOC（目录）
    """
    if not text:
        return ''
    
    md = markdown.Markdown(
        extensions=['toc'],
        extension_configs={
            'toc': {
                'toc_depth': 3,
                'title': '',
            }
        }
    )
    
    md.convert(text)
    return mark_safe(md.toc)


@register.filter(name='article_link')
def article_link_filter(text):
    """
    将 @[文章标题] 转换为超链接
    例如: @[如何使用Django] → <a href="/blog/how-to-use-django/">如何使用Django</a>
    
    支持在副标题、公告、博客文章内容中使用
    """
    if not text:
        return ''
    
    pattern = r'@\[([^\]]+)\]'
    
    def replace_link(match):
        title = match.group(1)
        try:
            article = Article.objects.filter(title__iexact=title, status='published').first()
            if article:
                return f'<a href="/blog/{article.slug}/">{title}</a>'
            return title
        except Exception:
            return title
    
    return mark_safe(re.sub(pattern, replace_link, text))
