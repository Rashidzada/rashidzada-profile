import re
from urllib.parse import parse_qs, urlparse

from django.conf import settings
from django.core.files.storage import default_storage
from django.templatetags.static import static


GOOGLE_DRIVE_HOSTS = {"drive.google.com", "docs.google.com"}


def extract_google_drive_file_id(url):
    parsed = urlparse(url.strip())
    if parsed.netloc not in GOOGLE_DRIVE_HOSTS:
        return ""

    query = parse_qs(parsed.query)
    if "id" in query and query["id"]:
        return query["id"][0]

    file_match = re.search(r"/file/d/([^/]+)", parsed.path)
    if file_match:
        return file_match.group(1)

    d_match = re.search(r"/d/([^/]+)", parsed.path)
    if d_match:
        return d_match.group(1)

    return ""


def normalize_image_source(value):
    if not value:
        return ""

    normalized = str(value).strip().replace("\\", "/")
    parsed = urlparse(normalized)

    if parsed.scheme in {"http", "https"}:
        file_id = extract_google_drive_file_id(normalized)
        if file_id:
            return f"https://drive.google.com/uc?export=view&id={file_id}"

    return normalized


def is_external_image_url(value):
    normalized = normalize_image_source(value)
    return normalized.startswith(("http://", "https://", "//"))


def is_media_asset(value):
    normalized = normalize_image_source(value)
    if not normalized:
        return False
    if normalized.startswith(("http://", "https://", "//", "/")):
        return normalized.startswith((settings.MEDIA_URL, "/media/"))
    if normalized.startswith("media/"):
        return True
    return default_storage.exists(normalized)


def resolve_image_src(value):
    normalized = normalize_image_source(value)
    if not normalized:
        return ""

    if normalized.startswith(("http://", "https://", "//")):
        return normalized

    if normalized.startswith("/"):
        return normalized

    if normalized.startswith("media/"):
        return f"{settings.MEDIA_URL.rstrip('/')}/{normalized.split('media/', 1)[1]}"

    if default_storage.exists(normalized):
        return default_storage.url(normalized)

    if normalized.startswith("static/"):
        return f"{settings.STATIC_URL.rstrip('/')}/{normalized.split('static/', 1)[1]}"

    return static(normalized)
