from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages

from .models import Tweet, Like, Comment, Follow, Profile, Notification
from .forms import TweetForm, UserRegistrationForm, TweetSearchForm, CommentForm, ProfileForm


def _notify(recipient, sender, notif_type, tweet=None):
    if recipient != sender:
        Notification.objects.create(
            recipient=recipient, sender=sender,
            notif_type=notif_type, tweet=tweet
        )


# ── Feed views ─────────────────────────────────────────────────────────────────

def tweet_list(request):
    tweets = Tweet.objects.select_related('user', 'user__profile', 'parent', 'parent__user').prefetch_related('likes', 'comments', 'retweets').all()
    paginator = Paginator(tweets, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'tweet_list.html', {'page_obj': page_obj})


@login_required
def feed(request):
    following_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
    tweets = Tweet.objects.filter(
        Q(user__in=following_ids) | Q(user=request.user)
    ).select_related('user', 'user__profile', 'parent', 'parent__user').prefetch_related('likes', 'comments', 'retweets')
    paginator = Paginator(tweets, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'feed.html', {'page_obj': page_obj})


# ── Tweet CRUD ─────────────────────────────────────────────────────────────────

@login_required
def tweet_create(request):
    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user
            tweet.save()
            messages.success(request, 'Tweet posted!')
            return redirect('tweet_list')
    else:
        form = TweetForm()
    return render(request, 'tweet_form.html', {'form': form})


@login_required
def tweet_edit(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id, user=request.user)
    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES, instance=tweet)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tweet updated!')
            return redirect('tweet_detail', tweet_id=tweet.id)
    else:
        form = TweetForm(instance=tweet)
    return render(request, 'tweet_form.html', {'form': form, 'tweet': tweet})


@login_required
def tweet_delete(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id, user=request.user)
    if request.method == 'POST':
        tweet.delete()
        messages.success(request, 'Tweet deleted.')
        return redirect('tweet_list')
    return render(request, 'tweet_confirm_delete.html', {'tweet': tweet})


def tweet_detail(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id)
    comments = tweet.comments.select_related('user', 'user__profile').all()
    comment_form = CommentForm()
    return render(request, 'tweet_detail.html', {
        'tweet': tweet,
        'comments': comments,
        'comment_form': comment_form,
    })


# ── Likes ──────────────────────────────────────────────────────────────────────

@login_required
def tweet_like(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id)
    like, created = Like.objects.get_or_create(user=request.user, tweet=tweet)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
        _notify(tweet.user, request.user, 'like', tweet)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'liked': liked, 'count': tweet.like_count()})
    return redirect(request.META.get('HTTP_REFERER', 'tweet_list'))


# ── Comments ───────────────────────────────────────────────────────────────────

@login_required
def tweet_comment(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.tweet = tweet
            comment.save()
            _notify(tweet.user, request.user, 'comment', tweet)
            messages.success(request, 'Comment added!')
    return redirect('tweet_detail', tweet_id=tweet_id)


@login_required
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, user=request.user)
    tweet_id = comment.tweet_id
    comment.delete()
    messages.success(request, 'Comment deleted.')
    return redirect('tweet_detail', tweet_id=tweet_id)


# ── Retweets ───────────────────────────────────────────────────────────────────

@login_required
def tweet_retweet(request, tweet_id):
    original = get_object_or_404(Tweet, pk=tweet_id)
    existing = Tweet.objects.filter(user=request.user, parent=original).first()
    if existing:
        existing.delete()
        retweeted = False
    else:
        Tweet.objects.create(user=request.user, text=original.text, parent=original)
        retweeted = True
        _notify(original.user, request.user, 'retweet', original)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'retweeted': retweeted, 'count': original.retweet_count()})
    return redirect(request.META.get('HTTP_REFERER', 'tweet_list'))


# ── Follow ─────────────────────────────────────────────────────────────────────

@login_required
def follow_user(request, username):
    target = get_object_or_404(User, username=username)
    if target == request.user:
        return redirect('profile', username=username)
    follow, created = Follow.objects.get_or_create(follower=request.user, following=target)
    if not created:
        follow.delete()
    else:
        _notify(target, request.user, 'follow')
    return redirect('profile', username=username)


# ── Profiles ───────────────────────────────────────────────────────────────────

def profile(request, username):
    user = get_object_or_404(User, username=username)
    profile_obj, _ = Profile.objects.get_or_create(user=user)
    tweets = Tweet.objects.filter(user=user).select_related('user').prefetch_related('likes', 'comments', 'retweets')
    paginator = Paginator(tweets, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    is_following = (
        request.user.is_authenticated and
        Follow.objects.filter(follower=request.user, following=user).exists()
    )
    return render(request, 'profile.html', {
        'profile_user': user,
        'profile_obj': profile_obj,
        'page_obj': page_obj,
        'is_following': is_following,
        'follower_count': profile_obj.follower_count(),
        'following_count': profile_obj.following_count(),
    })


@login_required
def profile_edit(request):
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated!')
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileForm(instance=profile_obj)
    return render(request, 'profile_edit.html', {'form': form})


# ── Search ─────────────────────────────────────────────────────────────────────

def tweet_search(request):
    form = TweetSearchForm(request.GET or None)
    tweets = None
    users = None
    if form.is_valid():
        query = form.cleaned_data.get('query', '').strip()
        if query:
            tweets = Tweet.objects.filter(text__icontains=query).select_related('user', 'user__profile').prefetch_related('likes', 'comments')
            users = User.objects.filter(
                Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query)
            ).select_related('profile')
    return render(request, 'tweet_search.html', {'form': form, 'tweets': tweets, 'users': users})


# ── Notifications ──────────────────────────────────────────────────────────────

@login_required
def notifications(request):
    notifs = request.user.notifications.select_related('sender', 'sender__profile', 'tweet').all()
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'notifications.html', {'notifications': notifs})


@login_required
def notifications_count(request):
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'count': count})


# ── Auth ───────────────────────────────────────────────────────────────────────

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            Profile.objects.create(user=user)
            login(request, user)
            messages.success(request, f'Welcome to TweetBar, {user.username}!')
            return redirect('tweet_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})
