# TweetBar v2.0

A full-featured Django microblogging platform.

## Features
- Post, edit, delete tweets with optional photo
- Like / Unlike (AJAX, no page reload)
- Comments with threaded view
- Retweets (with undo)
- User profiles (avatar, bio, website)
- Follow / Unfollow users
- Personal feed (tweets from followed users)
- Notifications (likes, comments, follows, retweets)
- Search (tweets + users)
- Pagination everywhere
- Dark theme UI (Bootstrap 5)

## Deploy to Railway

### 1. Set environment variables in Railway dashboard
| Variable | Value |
|---|---|
| `SECRET_KEY` | Long random string (https://djecrety.ir) |
| `DEBUG` | `False` |

Railway auto-injects `PORT` and `RAILWAY_PUBLIC_DOMAIN`.

### 2. Deploy
```bash
railway login
railway link
railway up
```

### 3. Create superuser (after first deploy)
```bash
railway run python manage.py createsuperuser
```

## Local development
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit http://127.0.0.1:8000
