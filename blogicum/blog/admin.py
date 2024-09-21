from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db import models

from .models import Category, Location, Post, Comment


class UserAdminCustom(UserAdmin):
    list_display = (
        'email', 'first_name', 'last_name', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser')
    search_fields = ('username', )
    birthday = models.DateField()

    @admin.display(
        description='Десятилетие года рождения'
    )
    def decade_born_in(self):
        decade = self.birthday.year // 10 * 10
        return f'{decade}’s'


admin.site.unregister(User)
admin.site.register(User, UserAdminCustom)


class PostInline(admin.StackedInline):
    model = Post
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = (PostInline,)
    list_display = ('title', 'description',)
    list_display_links = ('title',)
    search_fields = ('title',)


class LocationInline(admin.StackedInline):
    model = Post
    extra = 0


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    inlines = (PostInline,)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'text', 'category',
                    'pub_date', 'location', 'is_published', 'created_at',)
    search_fields = ('text',)
    list_editable = ('category', 'is_published', 'location')
    list_filter = ('created_at',)
    empty_value_display = ('-пусто-')
    list_display_links = ('title',)

# @admin.register(Comment)
# class CommentAdmin(admin.ModelAdmin):
#     list_display = ('text')


admin.site.register(Comment)
