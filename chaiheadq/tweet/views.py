from django.shortcuts import render
from .models import Tweet
from .forms import TweetForm, UserRegistrationForm, TweetSearchForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login


# Create your views here.
def index(request):
    return render(request, 'index.html')

## Listing of all tweets 
def tweet_list(request):
    tweets = Tweet.objects.all().order_by('-created_at')
    return  render(request, 'tweet_list.html', {'tweets': tweets})

@login_required
def tweet_create(request):
    if request.method == 'POST':
         form = TweetForm(request.POST, request.FILES)
         if form.is_valid():
             tweet = form.save(commit=False)
             tweet.user = request.user
             tweet.save()
             return redirect('tweet_list')
    else:
      form = TweetForm()
    return render(request, 'tweet_form.html', {'form': form})

@login_required
def tweet_edit(request,tweet_id ):
    tweet=get_object_or_404(Tweet, pk=tweet_id, user= request.user)
    if request.method=='POST':
        form = TweetForm(request.POST, request.FILES, instance=tweet)
        if form.is_valid():
            form.save(commit=False)
            tweet.user = request.user
            tweet.save()
            return redirect('tweet_list')
    else:
        form = TweetForm(instance=tweet)
    return render(request, 'tweet_form.html', {'form':form })

@login_required
def tweet_delete(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id, user= request.user)
    if request.method=='POST':
        tweet.delete()
        return redirect('tweet_list')
    else:
        return render(request, 'tweet_confirm_delete.html', )

  #[root] templates > [make] registration folder 

def register(request):
        if request.method == 'POST':
         form = UserRegistrationForm(request.POST)
         if form.is_valid():
             user = form.save(commit=False)
             user.set_password(form.cleaned_data['password1'])
             user.save()
             login(request, user)
         return redirect('tweet_list')
        
        else:
            form = UserRegistrationForm()

        return render(request, 'registration/register.html', {'form': form})



def tweet_search(request):
    form = TweetSearchForm(request.GET or None)
    tweets = None

    if form.is_valid():
        query = form.cleaned_data.get('query')
        if query:
            # Use Django ORM to filter tweets containing the search query
            tweets = Tweet.objects.filter(text__icontains=query)

    return render(request, 'tweet_search.html', {'form': form, 'tweets': tweets})