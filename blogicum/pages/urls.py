"""Импорт путей для конвертера из рабочей urls и view-функии."""
from django.urls import path
from django.views.generic import TemplateView

# from . import views

app_name = 'pages'

urlpatterns = [
    path(
        'about/',
        TemplateView.as_view(template_name='pages/about.html'),
        name='about'
    ),
    path(
        'rules/',
        TemplateView.as_view(template_name='pages/rules.html'),
        name='rules'
    ),
]
