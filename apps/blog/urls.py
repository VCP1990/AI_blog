from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.blog_list, name='list'),
    path('<slug:slug>/', views.article_detail, name='article_detail'),
    path('category/<slug:slug>/', views.category_detail, name='category'),
    path('tag/<slug:slug>/', views.tag_detail, name='tag'),
]
