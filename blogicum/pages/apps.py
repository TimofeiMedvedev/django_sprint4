"""Импорт модуля apps."""
from django.apps import AppConfig


class PagesConfig(AppConfig):
    """Класс BlogConfig для подключения приложения в settings."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pages'
