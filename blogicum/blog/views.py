from typing import Any, Dict

from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.http import Http404, HttpResponseForbidden
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .constants import POSTS_FOR_PAGINATOR
from .forms import CommentForm, PasswordChangeForm, PostForm
from .models import Category, Comment, Post

User = get_user_model()


class DirectionMixin(LoginRequiredMixin):

    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        if self.get_object().author != request.user:
            return redirect(
                'blog:post_detail',
                post_id=self.kwargs[self.pk_url_kwarg]
            )
        return super().dispatch(request, *args, **kwargs)


class UserProfileListView(ListView):

    template_name = 'blog/profile.html'
    paginate_by = POSTS_FOR_PAGINATOR

    def get_queryset(self) -> QuerySet[Any]:

        self.author = get_object_or_404(
            User,
            username=self.kwargs['username']
        )

        if self.author != self.request.user:
            return self.author.posts(manager='published').order_by('-pub_date')
        else:
            return self.author.posts.with_comment_count().order_by('-pub_date')

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    fields = (
        'username',
        'first_name',
        'last_name',
        'email',
    )

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )

    def get_object(self, queryset=None):
        return self.request.user


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


class PostsCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class EditPostView(DirectionMixin, UpdateView):

    model = Post
    pk_url_kwarg = 'post_id'
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={self.pk_url_kwarg: self.kwargs[self.pk_url_kwarg]}
        )


class DeletePostView(DirectionMixin, DeleteView):

    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user}
        )

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context


class PostListView(ListView):
    template_name = 'blog/index.html'
    paginate_by = POSTS_FOR_PAGINATOR

    def get_queryset(self) -> QuerySet[Any]:
        return Post.published.order_by('-pub_date')


class CategoryPostView(ListView):
    template_name = 'blog/category.html'
    paginate_by = POSTS_FOR_PAGINATOR

    def get_queryset(self) -> QuerySet[Any]:
        self.category = get_object_or_404(
            Category, is_published=True,
            slug=self.kwargs['category_slug'],
        )
        return self.category.posts(manager='published').order_by('-pub_date')

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class PostDetailView(DetailView):
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'
    model = Post

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().select_related(
            'author',
            'location',
            'category',
        )

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        if post.author != self.request.user and (
            post.is_published is False
            or post.category.is_published is False
            or post.pub_date > timezone.now()
        ):
            raise Http404
        return post

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related(
            'author'
        )
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
