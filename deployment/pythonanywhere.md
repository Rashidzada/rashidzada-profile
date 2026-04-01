**PythonAnywhere**
Set the project up with these steps:

1. Create or open a Python 3.14 virtual environment on PythonAnywhere.
2. Upload or clone this project into your home directory.
3. Install dependencies:
   `pip install -r requirements.txt`
4. Export the production environment variables from [.env.example](/c:/Users/RashidZada/Downloads/Personal/.env.example).
   Make sure these are set for admin access:
   `DJANGO_SUPERUSER_USERNAME`
   `DJANGO_SUPERUSER_EMAIL`
   `DJANGO_SUPERUSER_PASSWORD`
   For Snail Bot with DeepSeek, also set:
   `DEEPSEEK_API_KEY`
   `DEEPSEEK_BASE_URL`
   `DEEPSEEK_MODEL`
   Use only the hostname in `DJANGO_ALLOWED_HOSTS`.
   Correct: `rashidzada.pythonanywhere.com`
   Not valid for Django allowed hosts: `https://rashidzada.pythonanywhere.com/pythonnaywhere`
5. Run:
   `python manage.py migrate`
   `python manage.py ensure_superuser`
   `python manage.py seed_portfolio`
   `python manage.py collectstatic --noinput`
6. In the PythonAnywhere web app config, point the WSGI file to [config/wsgi.py](/c:/Users/RashidZada/Downloads/Personal/config/wsgi.py).
7. Add a static files mapping:
   URL: `/static/`
   Directory: `/home/yourusername/Personal/staticfiles`
8. Add a media files mapping for admin uploads and pasted image management:
   URL: `/media/`
   Directory: `/home/yourusername/Personal/media`
9. Reload the web app.

Admin login URL:
`https://yourusername.pythonanywhere.com/admin/`

Image handling in admin:
- Upload from your computer
- Paste a public image URL
- Paste a public Google Drive sharing URL
- Clear the current image if needed

Snail Bot:
- Uses the OpenAI SDK against DeepSeek when `DEEPSEEK_API_KEY` is configured
- Falls back to a local profile-only answer mode if the API key is missing
- Does not answer unrelated questions by design

For updates, run `python manage.py migrate`, `python manage.py ensure_superuser`, `python manage.py seed_portfolio` if content schema changed, then `python manage.py collectstatic --noinput`, and reload the app.
