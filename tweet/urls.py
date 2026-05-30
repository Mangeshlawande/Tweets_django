from django.urls import path
from . import views

urlpatterns = [
    path('', views.tweet_list, name='tweet_list'),
    path('feed/', views.feed, name='feed'),
    path('create/', views.tweet_create, name='tweet_create'),
    path('<int:tweet_id>/', views.tweet_detail, name='tweet_detail'),
    path('<int:tweet_id>/edit/', views.tweet_edit, name='tweet_edit'),
    path('<int:tweet_id>/delete/', views.tweet_delete, name='tweet_delete'),
    path('<int:tweet_id>/like/', views.tweet_like, name='tweet_like'),
    path('<int:tweet_id>/comment/', views.tweet_comment, name='tweet_comment'),
    path('<int:tweet_id>/retweet/', views.tweet_retweet, name='tweet_retweet'),
    path('comment/<int:comment_id>/delete/', views.comment_delete, name='comment_delete'),
    path('search/', views.tweet_search, name='tweet_search'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('profile/edit/me/', views.profile_edit, name='profile_edit'),
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/count/', views.notifications_count, name='notifications_count'),
    path('register/', views.register, name='register'),
]
