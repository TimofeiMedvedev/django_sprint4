"""Импорт путей для конвертера из рабочей urls и view-функии."""
from django.urls import path, include

from . import views

app_name = 'blog'

index = [path('', views.PostListView.as_view(), name='index'),]

posts = [
    path('create/', views.PostsCreateView.as_view(), name='create_post'),
    path(
        '<int:post_id>/edit/',
        views.EditPostView.as_view(),
        name='edit_post'
    ),
    path(
        '<int:post_id>/delete/',
        views.DeletePostView.as_view(),
        name='delete_post'
    ),
    path(
        '<int:post_id>/',
        views.PostDetailView.as_view(),
        name='post_detail',
    ),
    path('<int:post_id>/comment', views.add_comment, name='add_comment'),
    path(
        '<int:post_id>/edit_comment/<int:comment_id>/',
        views.edit_comment,
        name='edit_comment',
    ),
    path(
        '<int:post_id>/delete_comment/<int:comment_id>/',
        views.delete_comment,
        name='delete_comment',
    ),
]

profile = [
    path(
        '<username>/',
        views.UserProfileListView.as_view(),
        name='profile'),
    path(
        '',
        views.UserUpdateView.as_view(),
        name='edit_profile',
    ),
]

category = [
    path('<slug:category_slug>/', views.CategoryPostView.as_view(),
         name='category_posts'),
]

urlpatterns = [
    path('', include(index)),
    path('posts/', include(posts)),
    path('profile/', include(profile)),
    path('category/', include(category)),
]
