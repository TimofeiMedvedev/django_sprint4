"""Импорт функции render и Http404."""
from typing import Any
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from .forms import PostForm, UserForm, PasswordChangeForm, CommentForm
from django.contrib.auth import update_session_auth_hash
from .constants import NUMBER_POSTS, POSTS_FOR_PAGINATOR
from .models import Category, Post, Comment
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    CreateView, DeleteView, ListView, UpdateView, DetailView
)
from django.http import HttpResponseForbidden
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import Http404


User = get_user_model()


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.posts(manager='published').all()
    paginator = Paginator(posts, POSTS_FOR_PAGINATOR)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'profile': user,
        'page_obj': page_obj,
    }
    return render(request, 'blog/profile.html', context)


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:index', 
            kwargs={
                'username': self.request.user.username
            }
        )


@login_required
def password_change_view(request, username):
    user = request.user
    form = PasswordChangeForm(user, request.POST)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect('blog:password_change_done')
    else:
        form = PasswordChangeForm(user)
    context = {'form': form}
    return render(request, 'blog/password_change_form.html', context)



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


# @login_required
# def post_create(request):
#     template_name = 'blog/create.html'
#     form = PostForm(request.POST or None, files=request.FILES or None,)
#     if form.is_valid():
#         post = form.save(commit=False)
#         post.author = request.user
#         post.save()
#         return redirect('blog:index')
#     return render(request, template_name, {'form': form})
class PostsCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class EditPostView(LoginRequiredMixin, UpdateView):

    model = Post
    pk_url_kwarg = 'post_id'
    form_class = PostForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            return redirect('blog:post_detail', self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class DeletePostView(LoginRequiredMixin, DeleteView):

    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            return redirect(
                'blog:post_detail',
                self.kwargs.get('post_id')
            )
        return super().dispatch(request, *args, **kwargs)
    

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_object(self):
        object = super(PostDetailView, self).get_object()
        if self.request.user != object.author and (
            not object.is_published or not object.category.is_published
        ):
            raise Http404()
        return object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context
    
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author != request.user:
        return HttpResponseForbidden(
            'У вас нет прав для редактирования этого комментария.'
        )

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id)
    else:
        form = CommentForm(instance=comment)
    context = {
        'form': form,
        'comment': comment,
        'is_edit': True,
    }
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author != request.user:
        return HttpResponseForbidden(
            "У вас нет прав для удаления этого комментария."
        )

    if request.method == "POST":
        comment.delete()
        return redirect('blog:post_detail', post_id)

    context = {
        'comment': comment,
        'is_delete': True,
    }
    return render(request, 'blog/comment.html', context)