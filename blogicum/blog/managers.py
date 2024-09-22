from django.db import models
from django.utils.timezone import now
from django.db.models import Count


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
    
    def with_comment_count(self):
        return self.annotate(
            comment_count=Count('comments')
        )
    
    

class PublishedPostManager(models.Manager):
    def get_queryset(self) -> PostQuerySet:
        return (
            PostQuerySet(self.model)
            .with_related_data()
            .published()
            .with_comment_count()
        )


