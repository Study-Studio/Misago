from django.db import transaction
from django.utils import timezone

from .dates import get_cutoff_date
from .models import PostRead


def make_read_aware(user, target):
    if not target:
        return

    if hasattr(target, '__iter__'):
        make_posts_read_aware(user, target)
    else:
        make_posts_read_aware(user, [target])


def make_posts_read_aware(user, posts):
    make_read(posts)

    if user.is_anonymous:
        return

    cutoff_date = get_cutoff_date(user)
    unresolved_posts = {}

    for post in posts:
        if post.posted_on > cutoff_date:
            post.is_read = False
            post.is_new = True
            unresolved_posts[post.pk] = post

    if unresolved_posts:
        queryset = user.postread_set.filter(post__in=unresolved_posts)
        for post_id in queryset.values_list('post_id', flat=True):
            unresolved_posts[post_id].is_read = True
            unresolved_posts[post_id].is_new = False


def make_read(posts):
    for post in posts:
        post.is_read = True
        post.is_new = False


def save_read(user, post):
    user.postread_set.create(
        category=post.category,
        thread=post.thread,
        post=post,
    )


def delete_reads(post):
    post.postread_set.all().delete()
