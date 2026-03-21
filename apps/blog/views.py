from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.conf import settings
from django.utils.translation import get_language as django_get_language

from apps.blog.models import Article
from apps.categories.models import Category
from apps.tags.models import Tag


def get_language(request=None):
    """从 URL 路径获取当前语言"""
    if request:
        path = request.path_info
        if path.startswith('/zh/'):
            return 'zh'
    return django_get_language() or 'en'


def blog_list(request: HttpRequest) -> HttpResponse:
    language = get_language(request)
    articles = Article.objects.filter(status='published', language=language).order_by('-published_at')
    
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
    language = get_language() or 'en'
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


def category_detail(request: HttpRequest, slug: str) -> HttpResponse:
    language = get_language() or 'en'
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
    language = get_language() or 'en'
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
