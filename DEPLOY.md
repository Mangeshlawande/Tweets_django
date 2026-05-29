# 🚂 Deploy to Railway — ChaiHeadQ Tweet App

## Files Generated

| File | Purpose |
|---|---|
| `Dockerfile` | Replaces the dev Dockerfile — runs `collectstatic`, uses gunicorn |
| `start.sh` | Runs `migrate` then starts gunicorn on Railway's `$PORT` |
| `requirements.txt` | Adds `gunicorn` + `whitenoise` |
| `settings.py` | Replaces `chaiheadq/settings.py` — reads env vars, adds WhiteNoise |
| `railway.toml` | Tells Railway to use the Dockerfile and call `start.sh` |

---

## Step-by-step deployment

### 1. Copy generated files into your project

```
play/chaiheadq/
├── Dockerfile          ← replace with the generated one
├── start.sh            ← new file (chmod +x it locally too)
├── requirements.txt    ← replace
├── railway.toml        ← new file (lives alongside Dockerfile)
└── chaiheadq/
    └── settings.py     ← replace
```

### 2. Set environment variables in Railway

Go to your Railway project → **Variables** tab and add:

| Variable | Value |
|---|---|
| `SECRET_KEY` | A long random string (use https://djecrety.ir) |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | Leave blank — Railway domain is auto-added by settings.py |

Railway automatically injects `PORT` and `RAILWAY_PUBLIC_DOMAIN` — no action needed.

### 3. Deploy

```bash
# Push to GitHub, then connect the repo in Railway
# OR deploy directly with the Railway CLI:
railway login
railway link         # select your project
railway up
```

### 4. After first deploy — create a superuser

```bash
railway run python manage.py createsuperuser
```

---

## ⚠️ SQLite caveat

Railway's filesystem is **ephemeral** — any uploaded photos and SQLite data are wiped on each deploy/restart.

**For persistence, add Railway's Postgres plugin:**

1. Railway dashboard → **+ New** → **Database** → **PostgreSQL**
2. Add to `requirements.txt`: `psycopg2-binary==2.9.10` and `dj-database-url==2.3.0`
3. Replace the `DATABASES` block in `settings.py`:

```python
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
    )
}
```

4. For media uploads use **Cloudinary** or **AWS S3** with `django-storages`.

---

## How to extend the app

### Add likes / retweets
Create a `Like` model with a ManyToMany to `Tweet` and `User`, add a view + URL, and render a heart button in `tweet_list.html`.

### Add comments
New `Comment` model with FK to `Tweet`, a small form, and a detail view (`tweet_detail`) where the comment list lives.

### Add pagination
In `tweet_list` view: `tweets = Tweet.objects.all().order_by('-created_at')` → wrap with `Paginator(tweets, 10)` and pass `page_obj` to the template.

### Add user profiles
Create a `Profile` model (OneToOne with User), add a profile picture field, and a profile page view.

### Add an API (REST)
Install `djangorestframework`, create a `serializers.py` and an `api/` URL namespace exposing JSON endpoints — useful if you want a mobile app later.
