from django.contrib.auth import get_user_model
from django.db import models

from .constants import MAX_LENGTH_FIELD
from .managers import PostQuerySet, PublishedPostManager

User = get_user_model()


class BaseCreated(models.Model):

    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True,
    )

    class Meta:
        abstract = True
        ordering = ('created_at', )


class BasePublished(BaseCreated):
    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )

    class Meta:
        abstract = True


class Location(BasePublished):
    name = models.CharField('Название места', max_length=MAX_LENGTH_FIELD)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Category(BasePublished):
    title = models.CharField('Заголовок', max_length=MAX_LENGTH_FIELD)
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        help_text='Идентификатор страницы для URL; разрешены символы '
                  'латиницы, цифры, дефис и подчёркивание.',

        unique=True,
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Post(BasePublished):
    title = models.CharField('Заголовок', max_length=MAX_LENGTH_FIELD)
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text='Если установить дату и время в будущем — '
                  'можно делать отложенные публикации.'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория'
    )
    image = models.ImageField(
        verbose_name='Картинка у публикации',
        upload_to='post_images',
        blank=True
    )

    objects = PostQuerySet.as_manager()
    published = PublishedPostManager()

    class Meta:
        default_related_name = 'posts'
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date', )

    def __str__(self):
        return self.title


class Comment(BaseCreated):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария',
    )

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Комментируемый пост',
    )

    text = models.TextField(verbose_name='Текст комментария')

    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True,
    )

    class Meta:
        default_related_name = 'comments'
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at', )

    def __str__(self):
        return self.text
