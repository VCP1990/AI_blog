from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from apps.core.models import SiteSettings, HeroPage, Announcement
from django.conf import settings
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.syndication.views import Feed
from django.utils import timezone
from django.utils.translation import get_language

from apps.blog.models import Article
from apps.categories.models import Category
from apps.tags.models import Tag


def get_current_language(request=None):
    """从 URL 路径获取当前语言"""
    if request:
        path = request.path_info
        if path.startswith('/zh-hans/') or path.startswith('/zh_Hans/'):
            return 'zh-hans'
    return get_language() or 'en'


def home(request: HttpRequest) -> HttpResponse:
    language = get_current_language(request)
    hero_page = HeroPage.get_active(language)
    
    if hero_page:
        content_blocks = hero_page.content_blocks.filter(is_active=True).order_by('order')
        cta = getattr(hero_page, 'cta', None)
        context = {
            'hero': hero_page,
            'content_blocks': content_blocks,
            'cta': cta if cta and cta.is_active else None,
        }
        return render(request, 'hero/index_dynamic.html', context)
    return render(request, 'hero/index.html')


def blog_list(request: HttpRequest) -> HttpResponse:
    language = get_current_language(request)
    articles = Article.objects.filter(status='published', language=language).select_related('category').order_by('-published_at')
    paginator = Paginator(articles, settings.ARTICLES_PER_PAGE)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.filter(is_active=True, language=language)
    tags = Tag.objects.filter(is_active=True, language=language)
    popular_articles = Article.objects.filter(status='published', language=language).order_by('-views')[:5]
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'tags': tags,
        'popular_articles': popular_articles,
    }
    return render(request, 'blog/list.html', context)


def article_detail(request: HttpRequest, slug: str) -> HttpResponse:
    language = get_current_language()
    article = get_object_or_404(Article, slug=slug, status='published', language=language)
    article.increase_views()
    
    related_articles = Article.objects.filter(
        status='published',
        language=language,
        category=article.category
    ).exclude(pk=article.pk)[:3]
    
    categories = Category.objects.filter(is_active=True, language=language)
    tags = Tag.objects.filter(is_active=True, language=language)
    popular_articles = Article.objects.filter(status='published', language=language).order_by('-views')[:5]
    
    context = {
        'article': article,
        'related_articles': related_articles,
        'categories': categories,
        'tags': tags,
        'popular_articles': popular_articles,
    }
    return render(request, 'blog/detail.html', context)


def search(request: HttpRequest) -> HttpResponse:
    language = get_current_language()
    query = request.GET.get('q', '').strip()
    articles = Article.objects.filter(status='published', language=language)
    
    if query:
        articles = articles.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(summary__icontains=query)
        ).distinct()
    
    paginator = Paginator(articles, settings.ARTICLES_PER_PAGE)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.filter(is_active=True, language=language)
    tags = Tag.objects.filter(is_active=True, language=language)
    popular_articles = Article.objects.filter(status='published', language=language).order_by('-views')[:5]
    
    context = {
        'query': query,
        'page_obj': page_obj,
        'categories': categories,
        'tags': tags,
        'popular_articles': popular_articles,
        'total_results': paginator.count if query else 0,
    }
    return render(request, 'blog/search.html', context)


def category_detail(request: HttpRequest, slug: str) -> HttpResponse:
    language = get_current_language()
    category = get_object_or_404(Category, slug=slug, is_active=True, language=language)
    articles = Article.objects.filter(
        status='published',
        language=language,
        category=category
    ).order_by('-published_at')
    
    paginator = Paginator(articles, settings.ARTICLES_PER_PAGE)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.filter(is_active=True, language=language)
    tags = Tag.objects.filter(is_active=True, language=language)
    popular_articles = Article.objects.filter(status='published', language=language).order_by('-views')[:5]
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'categories': categories,
        'tags': tags,
        'popular_articles': popular_articles,
    }
    return render(request, 'blog/category.html', context)


def tag_detail(request: HttpRequest, slug: str) -> HttpResponse:
    language = get_current_language()
    tag = get_object_or_404(Tag, slug=slug, is_active=True, language=language)
    articles = Article.objects.filter(
        status='published',
        language=language,
        tags=tag
    ).order_by('-published_at')
    
    paginator = Paginator(articles, settings.ARTICLES_PER_PAGE)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.filter(is_active=True, language=language)
    tags = Tag.objects.filter(is_active=True, language=language)
    popular_articles = Article.objects.filter(status='published', language=language).order_by('-views')[:5]
    
    context = {
        'tag': tag,
        'page_obj': page_obj,
        'categories': categories,
        'tags': tags,
        'popular_articles': popular_articles,
    }
    return render(request, 'blog/tag.html', context)


def about(request: HttpRequest) -> HttpResponse:
    language = get_current_language()
    settings_obj = SiteSettings.get_settings(language)
    context = {
        'settings': settings_obj,
    }
    return render(request, 'landing/about.html', context)


class LatestArticlesFeed(Feed):
    def get_object(self, request):
        return get_language() or 'en'
    
    def title(self, obj):
        return "AI Blog" if obj == 'en' else "AI 博客"
    
    def link(self, obj):
        return f"/{obj}/blog/"
    
    def description(self, obj):
        return "Latest articles from AI Blog" if obj == 'en' else "AI 博客最新文章"
    
    def items(self, obj):
        return Article.objects.filter(status='published', language=obj).order_by('-published_at')[:20]
    
    def item_title(self, item):
        return item.title
    
    def item_description(self, item):
        return item.get_summary()
    
    def item_link(self, item):
        return reverse('blog:article_detail', args=[item.slug])
    
    def item_pubdate(self, item):
        return item.published_at
