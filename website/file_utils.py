from urllib.parse import urlparse

from django.conf import settings
from django.core.files.storage import default_storage
from django.templatetags.static import static

from .image_utils import extract_google_drive_file_id


def normalize_document_source(value):
    if not value:
        return ""

    normalized = str(value).strip().replace("\\", "/")
    parsed = urlparse(normalized)

    if parsed.scheme in {"http", "https"}:
        file_id = extract_google_drive_file_id(normalized)
        if file_id:
            return f"https://drive.google.com/file/d/{file_id}/view"

    return normalized


def is_external_document_url(value):
    normalized = normalize_document_source(value)
    return normalized.startswith(("http://", "https://", "//"))


def resolve_document_src(value):
    normalized = normalize_document_source(value)
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


def resolve_document_view_url(value):
    normalized = normalize_document_source(value)
    if not normalized:
        return ""

    file_id = extract_google_drive_file_id(normalized)
    if file_id:
        return f"https://drive.google.com/file/d/{file_id}/view"

    return resolve_document_src(normalized)


def resolve_document_download_url(value):
    normalized = normalize_document_source(value)
    if not normalized:
        return ""

    file_id = extract_google_drive_file_id(normalized)
    if file_id:
        return f"https://drive.google.com/uc?export=download&id={file_id}"

    return resolve_document_src(normalized)
