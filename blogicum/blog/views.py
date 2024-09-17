"""Импорт функции render и Http404."""
from django.shortcuts import get_object_or_404, render

from .constants import NUMBER_POSTS
from .models import Category, Post


def index(request):
    """View-функция для главной страницы."""
    posts = Post.published.all()[:NUMBER_POSTS]
    return render(request, 'blog/index.html', {'page_obj': posts})


def post_detail(request, post_id):
    """View-функция для страницы из словаря."""
    post = get_object_or_404(Post.published, id=post_id)
    return render(request, 'blog/detail.html', {'post': post})


def category_posts(request, category_slug):
    """View-функция для страницы категории."""
    category = get_object_or_404(
        Category, is_published=True,
        slug=category_slug,
    )
    posts = category.posts(manager='published').all()

    context = {'category': category, 'post_list': posts}
    return render(request, 'blog/category.html', context)
