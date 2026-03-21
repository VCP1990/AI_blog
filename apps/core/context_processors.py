from django.utils.translation import get_language
from apps.core.models import SiteSettings, Announcement


def site_settings(request):
    language = get_language() or 'en'
    return {'site_settings': SiteSettings.get_settings(language)}


def announcements(request):
    """添加活跃公告到全局上下文"""
    language = get_language() or 'en'
    active_announcements = Announcement.objects.filter(is_active=True, language=language)
    return {'announcements': active_announcements}
