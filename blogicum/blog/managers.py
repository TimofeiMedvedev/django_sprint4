from django.db import models
from django.utils.timezone import now


class PostQuerySet(models.QuerySet):
    def with_related_data(self):
        return self.select_related(
            'author',
            'category',
            'location',
        )

    def published(self):
        return self.filter(
            is_published=True,
            pub_date__lt=now(),
            category__is_published=True
        )


class PublishedPostManager(models.Manager):
    def get_queryset(self) -> PostQuerySet:
        return (
            PostQuerySet(self.model)
            .with_related_data()
            .published()
        )


class PublishedPostManager2(models.Manager):
    def get_queryset(self) -> PostQuerySet:
        return (
            PostQuerySet(self.model)
            .with_related_data()
        )
