from pathlib import Path
from uuid import uuid4

from django.core.files.storage import default_storage
from django.utils.html import format_html
from django.utils.text import slugify

from .file_utils import resolve_document_download_url, resolve_document_view_url


def save_admin_uploaded_file(uploaded_file, folder):
    file_suffix = Path(uploaded_file.name).suffix.lower() or ".pdf"
    base_name = slugify(Path(uploaded_file.name).stem)[:60] or "document"
    unique_name = f"{base_name}-{uuid4().hex[:10]}{file_suffix}"
    return default_storage.save(f"uploads/{folder}/{unique_name}", uploaded_file)


def render_admin_file_link(obj, field_name, label):
    if not obj or not getattr(obj, "pk", None):
        return "Save first to manage the file."

    raw_value = getattr(obj, field_name, "")
    view_url = resolve_document_view_url(raw_value)
    download_url = resolve_document_download_url(raw_value)
    if not view_url:
        return "No file set."

    return format_html(
        (
            '<div style="display:flex; flex-direction:column; gap:10px;">'
            '<div style="font-weight:700;">{}</div>'
            '<div style="display:flex; flex-wrap:wrap; gap:10px;">'
            '<a href="{}" target="_blank" rel="noopener" '
            'style="padding:8px 14px; border-radius:999px; background:#18d26e; color:#08110c; font-weight:700;">View</a>'
            '<a href="{}" target="_blank" rel="noopener" '
            'style="padding:8px 14px; border-radius:999px; background:#1f2937; color:#fff; font-weight:700;">Download</a>'
            "</div>"
            '<div style="font-size:12px; line-height:1.5; word-break:break-all; opacity:0.85;">{}</div>'
            "</div>"
        ),
        label,
        view_url,
        download_url,
        raw_value,
    )
