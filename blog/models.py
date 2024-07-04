from django.db import models
from django.contrib.auth.models import User


class MyUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    username = models.CharField(max_length=100)
    # password = models.CharField(max_length=10)
    full_name = models.CharField(max_length=150, null=True, blank=True)
    image = models.ImageField(upload_to='author/', default='author/149071.png')
    follower_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    post_count = models.PositiveIntegerField(default=0)
    bio = models.CharField(max_length=200, default='...')

    def __str__(self):
        return self.user.username


class Post(models.Model):
    author = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='post/')
    comment_count = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    like_count = models.IntegerField(default=0)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)


class CommentPost(models.Model):
    author = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class LikePost(models.Model):
    author = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class FollowMyUser(models.Model):
    follower = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='follower_user', blank=True, null=True)
    following = models.ForeignKey(MyUser, on_delete=models.CASCADE)
