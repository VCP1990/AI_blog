from django.urls import path
from django.views.i18n import set_language
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('search/', views.search, name='search'),
    path('rss/', views.LatestArticlesFeed(), name='rss'),
]
