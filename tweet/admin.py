from django.contrib import admin
from .models import Tweet, Like, Comment, Follow, Profile, Notification

admin.site.register(Tweet)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(Follow)
admin.site.register(Profile)
admin.site.register(Notification)
