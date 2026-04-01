# Rashid Zada Profile

A production-oriented Django profile/portfolio project for Rashid Zada. The site keeps the original frontend design but runs on real Django views, models, admin, seed data, and PythonAnywhere-friendly settings.

## What is included

- Real Django project with clean routes and database-backed content
- Seeded portfolio/profile data from the CV
- Custom Django admin branding as `Rashid Zada Profile`
- Admin superuser bootstrap command for local use and deployment
- Image management that supports:
  - upload from computer
  - public image URL
  - public Google Drive sharing URL
  - clearing an existing image
- Frontend image rendering that supports:
  - static seeded assets
  - uploaded media files
  - external URLs
  - Google Drive URLs
- JSON APIs for the profile, services, projects, and other seeded portfolio content
- `Snail Bot`, a profile-only assistant with a DeepSeek/OpenAI SDK integration and a local fallback mode
- Streamed Snail Bot replies for a more natural live-chat feel
- PythonAnywhere deployment helpers and env-based production settings

## Main URLs

- Site: `http://127.0.0.1:8000/`
- Admin: `http://127.0.0.1:8000/admin/`
- Full profile API: `http://127.0.0.1:8000/api/profile/`
- Snail Bot chat API: `http://127.0.0.1:8000/api/snail-bot/chat/`
- Snail Bot stream API: `http://127.0.0.1:8000/api/snail-bot/stream/`

## Project structure

- [config/settings.py](/c:/Users/RashidZada/Downloads/Personal/config/settings.py)
- [config/urls.py](/c:/Users/RashidZada/Downloads/Personal/config/urls.py)
- [website/models.py](/c:/Users/RashidZada/Downloads/Personal/website/models.py)
- [website/views.py](/c:/Users/RashidZada/Downloads/Personal/website/views.py)
- [website/admin.py](/c:/Users/RashidZada/Downloads/Personal/website/admin.py)
- [website/management/commands/seed_portfolio.py](/c:/Users/RashidZada/Downloads/Personal/website/management/commands/seed_portfolio.py)
- [website/management/commands/ensure_superuser.py](/c:/Users/RashidZada/Downloads/Personal/website/management/commands/ensure_superuser.py)
- [deployment/pythonanywhere.md](/c:/Users/RashidZada/Downloads/Personal/deployment/pythonanywhere.md)

## Local setup

1. Create and activate a virtual environment.
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Run migrations:
```bash
python manage.py migrate
```
4. Create the admin user:
```bash
python manage.py ensure_superuser --username admin --email you@example.com --password "ChangeThisPassword123!"
```
5. Seed the portfolio:
```bash
python manage.py seed_portfolio
```
6. Run the dev server:
```bash
python manage.py runserver
```

## Using your profile image in seed data

To regenerate the profile/favicons/hero image set from a local photo:

```bash
python manage.py seed_portfolio --profile-source "C:\path\to\your-photo.png"
```

This generates image assets inside the static site image folder and updates the seeded site configuration.

## Django admin image management

The image-backed admin models support both upload and URL workflows:

- Site configuration
- Profile highlights
- Services
- Projects
- Project gallery images

For each image field, admin now provides:

- current preview
- upload input
- URL input
- clear checkbox

### Google Drive support

You can paste a public Google Drive sharing link such as:

- `https://drive.google.com/file/d/FILE_ID/view?usp=sharing`
- `https://drive.google.com/open?id=FILE_ID`

The admin normalizes it into a direct image URL automatically.

Important: the Google Drive file must be public, otherwise the browser cannot render it on the site.

## Frontend image behavior

Frontend templates now resolve image sources automatically. A stored image value can be:

- a seeded static asset path like `assets/img/portfolio/portfolio-1.webp`
- an uploaded media path like `uploads/projects/cards/example.png`
- a public URL
- a Google Drive sharing URL

No template changes are needed when switching between these source types.

## Environment variables

Copy values from [.env.example](/c:/Users/RashidZada/Downloads/Personal/.env.example).
This project automatically loads local values from `.env` if that file exists.

Important variables:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- `DJANGO_SUPERUSER_USERNAME`
- `DJANGO_SUPERUSER_EMAIL`
- `DJANGO_SUPERUSER_PASSWORD`
- `DEEPSEEK_API_KEY`
- `DEEPSEEK_BASE_URL`
- `DEEPSEEK_MODEL`
- `PORTFOLIO_PROFILE_SOURCE`

### Allowed hosts note

For Django, `ALLOWED_HOSTS` must contain only the hostname.

Correct:

- `rashidzada.pythonanywhere.com`

Not correct:

- `https://rashidzada.pythonanywhere.com/pythonnaywhere`

Paths and protocols are not valid in `ALLOWED_HOSTS`.

## PythonAnywhere deployment

See the full guide in [deployment/pythonanywhere.md](/c:/Users/RashidZada/Downloads/Personal/deployment/pythonanywhere.md).

Short version:

1. Upload or clone the repo.
2. Install dependencies.
3. Set environment variables.
4. Run:
```bash
python manage.py migrate
python manage.py ensure_superuser
python manage.py seed_portfolio
python manage.py collectstatic --noinput
```
5. Map static files:
```text
/static/ -> /home/yourusername/Personal/staticfiles
```
6. Map media files:
```text
/media/ -> /home/yourusername/Personal/media
```
7. Reload the web app.

## Profile APIs

This project exposes JSON endpoints for the seeded Django content. Main endpoints:

- `GET /api/profile/`
- `GET /api/site-configuration/`
- `GET /api/page-intros/`
- `GET /api/social-links/`
- `GET /api/typed-roles/`
- `GET /api/about-facts/`
- `GET /api/statistics/`
- `GET /api/skills/`
- `GET /api/certifications/`
- `GET /api/languages/`
- `GET /api/strengths/`
- `GET /api/profile-highlights/`
- `GET /api/education/`
- `GET /api/experiences/`
- `GET /api/services/`
- `GET /api/services/<slug>/`
- `GET /api/project-categories/`
- `GET /api/projects/`
- `GET /api/projects/<slug>/`

Each endpoint returns a JSON object with `ok` and `data`.

## Snail Bot

`Snail Bot` is the floating site assistant. It only answers profile-related questions about Rashid Zada.

- If `DEEPSEEK_API_KEY` is set, Snail Bot uses the OpenAI SDK against DeepSeek.
- If the key is missing or the provider is unavailable, Snail Bot falls back to a local profile-aware responder.
- Unrelated questions are rejected on purpose so the assistant stays focused on the portfolio.

Chat endpoint:

```bash
curl -X POST http://127.0.0.1:8000/api/snail-bot/chat/ \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"What services does Rashid offer?\"}"
```

Example response shape:

```json
{
  "ok": true,
  "data": {
    "assistant": "Snail Bot",
    "related": true,
    "mode": "local",
    "message": "Rashid Zada offers these services: ..."
  }
}
```

Stream endpoint:

```bash
curl -X POST http://127.0.0.1:8000/api/snail-bot/stream/ \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"Tell me about Rashid's projects\"}"
```

## Verification commands

```bash
python manage.py check
python manage.py test
python manage.py collectstatic --noinput
```

## Git

If you want to push this project to GitHub:

```bash
git init
git add .
git commit -m "Initial Django profile project"
git branch -M main
git remote add origin https://github.com/Rashidzada/rashidzada-profile.git
git push -u origin main
```

If the remote already exists, update it with:

```bash
git remote set-url origin https://github.com/Rashidzada/rashidzada-profile.git
```
