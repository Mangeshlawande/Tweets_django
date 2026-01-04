# Tweets_django
Q. Learn how to lock  the view .
Q. Django built form 
Q. How to Perform Custom user Registration
Q. How to Perform Custom user login
Q. How to Perform Custom user logout

*Goal* : To Know  the flow of the framework and how to create a simple app using django framework.
## Installation
1. Install Python from [python.org](https://www.python.org/downloads/).
2. Install Django using pip:
   ```bash
   pip install django
   ```
3. Create a new Django project:
   ```bash
   django-admin startproject myproject
   ```
4. Navigate to the project directory:
   ```bash
   cd myproject
   ```      
5. Create a new Django app:
   ```bash
   python manage.py startapp tweets
   ```
6. Add the app to the `INSTALLED_APPS` list in `settings.py`:
   ```python
   INSTALLED_APPS = [
       ...,
       'tweets',
   ]
   ```
7. Create templates and static directories for your app.
8. Set up URLs in `urls.py` to route to your app's views.       
9. Run the development server:
   ```bash

   python manage.py makemigrations
   python manage.py migrate
   python manage.py runserver
   ```
10. create a superuser to access the admin panel:
   ```bash
   python manage.py createsuperuser
   ```
media_url and media_root settings in settings.py file
  ```python
  MEDIA_URL = '/media/'
  MEDIA_ROOT = BASE_DIR / 'media'
  ```
11. In your project's main `urls.py`, add the following to serve media files during development:
   ```python

static_url and static_root settings in settings.py file
  ```python
  STATIC_URL = '/static/'
  STATIC_ROOT = BASE_DIR / 'staticfiles'
  ```
   from django.conf import settings
   from django.conf.urls.static import static

   urlpatterns = [
       ...
   ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
   ```

   make model tweet in models.py file of tweets app
   migrate the model
   ```bash
   python manage.py makemigrations tweets
   python manage.py migrate
    ```
    register the model in admin.py file of tweets app

    create forms.py file in tweets app for user registration and login forms

    
