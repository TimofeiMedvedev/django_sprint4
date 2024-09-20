from django.contrib.auth import get_user_model
from django.db import models

from .constants import MAX_LENGTH_FIELD
from .managers import PostQuerySet, PublishedPostManager
from django.urls import reverse

User = get_user_model()


class BaseBlogModel(models.Model):
    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True,
    )

    class Meta:
        abstract = True
        ordering = ('created_at', )


class Location(BaseBlogModel):
    name = models.CharField('Название места', max_length=MAX_LENGTH_FIELD)

    class Meta(BaseBlogModel.Meta):
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Category(BaseBlogModel):
    title = models.CharField('Заголовок', max_length=MAX_LENGTH_FIELD)
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        help_text='Идентификатор страницы для URL; разрешены символы '
                  'латиницы, цифры, дефис и подчёркивание.',

        unique=True,
    )

    class Meta(BaseBlogModel.Meta):
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Post(BaseBlogModel):
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

    class Meta(BaseBlogModel.Meta):
        default_related_name = 'posts'
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date', )

    # def get_absolute_url(self):
    #     return reverse('blog:profile', args=[self.author])
    # def get_absolute_url(self):
    #     return reverse('blog:post_detail', args=(self.pk,))
    
    def comment_count(self):
        return self.comments.count()

    
    def __str__(self):
        return self.title
    

class Comment(BaseBlogModel):
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

    class Meta(BaseBlogModel.Meta):
        default_related_name = 'comments'
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at', )

    def __str__(self):
        return self.text