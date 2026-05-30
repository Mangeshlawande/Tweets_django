from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=300, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} Profile'

    def follower_count(self):
        return Follow.objects.filter(following=self.user).count()

    def following_count(self):
        return Follow.objects.filter(follower=self.user).count()


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_set')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower_set')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f'{self.follower.username} → {self.following.username}'


class Tweet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tweets')
    text = models.TextField(max_length=280)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='retweets'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.text[:30]}'

    def like_count(self):
        return self.likes.count()

    def comment_count(self):
        return self.comments.count()

    def retweet_count(self):
        return self.retweets.count()

    def is_liked_by(self, user):
        if not user.is_authenticated:
            return False
        return self.likes.filter(user=user).exists()

    def is_retweeted_by(self, user):
        if not user.is_authenticated:
            return False
        return self.retweets.filter(user=user).exists()


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'tweet')


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField(max_length=280)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.user.username}: {self.text[:30]}'


class Notification(models.Model):
    NOTIF_TYPES = [
        ('like', 'liked your tweet'),
        ('comment', 'commented on your tweet'),
        ('follow', 'started following you'),
        ('retweet', 'retweeted your tweet'),
    ]
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notif_type = models.CharField(max_length=20, choices=NOTIF_TYPES)
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
