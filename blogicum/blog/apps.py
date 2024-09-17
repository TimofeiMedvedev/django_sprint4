"""Импорт модуля apps."""
from django.apps import AppConfig


class BlogConfig(AppConfig):
    """Класс BlogConfig для подключения приложения в settings."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'
    verbose_name = 'Блог'
