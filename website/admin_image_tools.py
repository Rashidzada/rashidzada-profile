from pathlib import Path
from uuid import uuid4

from django import forms
from django.core.files.storage import default_storage
from django.utils.html import format_html
from django.utils.text import slugify

from .image_utils import is_external_image_url, normalize_image_source, resolve_image_src


DEFAULT_UPLOAD_HELP = "Upload an image from your computer."
DEFAULT_URL_HELP = "Paste a public image URL or a Google Drive sharing link."


def save_admin_uploaded_image(uploaded_file, folder):
    file_suffix = Path(uploaded_file.name).suffix.lower() or ".png"
    base_name = slugify(Path(uploaded_file.name).stem)[:60] or "image"
    unique_name = f"{base_name}-{uuid4().hex[:10]}{file_suffix}"
    return default_storage.save(f"uploads/{folder}/{unique_name}", uploaded_file)


def build_image_admin_form(model, image_fields):
    attrs = {}
    meta_exclude = []

    for field_name, config in image_fields.items():
        label = config.get("label", field_name.replace("_", " ").title())
        attrs[f"{field_name}_upload"] = forms.ImageField(
            required=False,
            label=f"{label} upload",
            help_text=config.get("upload_help", DEFAULT_UPLOAD_HELP),
        )
        attrs[f"{field_name}_url_input"] = forms.URLField(
            required=False,
            label=f"{label} URL",
            help_text=config.get("url_help", DEFAULT_URL_HELP),
        )
        attrs[f"{field_name}_clear"] = forms.BooleanField(
            required=False,
            label=f"Clear {label.lower()}",
        )
        meta_exclude.append(field_name)

    attrs["Meta"] = type(
        "Meta",
        (),
        {
            "model": model,
            "exclude": tuple(meta_exclude),
        },
    )

    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        self._resolved_image_values = {}
        for field_name in image_fields:
            current_value = normalize_image_source(getattr(self.instance, field_name, ""))
            if is_external_image_url(current_value):
                self.fields[f"{field_name}_url_input"].initial = current_value

    def clean(self):
        cleaned_data = forms.ModelForm.clean(self)
        self._resolved_image_values = {}

        for field_name, config in image_fields.items():
            upload_value = cleaned_data.get(f"{field_name}_upload")
            url_value = (cleaned_data.get(f"{field_name}_url_input") or "").strip()
            clear_value = cleaned_data.get(f"{field_name}_clear")
            current_value = getattr(self.instance, field_name, "")

            if clear_value and (upload_value or url_value):
                self.add_error(
                    f"{field_name}_clear",
                    "Use clear by itself, or provide a new upload/URL.",
                )
                continue

            if upload_value and url_value:
                self.add_error(
                    f"{field_name}_url_input",
                    "Use either upload or URL, not both.",
                )
                continue

            if clear_value:
                resolved_value = ""
            elif upload_value:
                resolved_value = save_admin_uploaded_image(upload_value, config["folder"])
            elif url_value:
                resolved_value = normalize_image_source(url_value)
            else:
                resolved_value = current_value

            self._resolved_image_values[field_name] = resolved_value

        return cleaned_data

    def save(self, commit=True):
        instance = forms.ModelForm.save(self, commit=False)
        for field_name, resolved_value in self._resolved_image_values.items():
            setattr(instance, field_name, resolved_value)
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    attrs["__init__"] = __init__
    attrs["clean"] = clean
    attrs["save"] = save

    form_class = type(f"{model.__name__}ImageAdminForm", (forms.ModelForm,), attrs)
    return form_class


def render_admin_image_preview(obj, field_name, label):
    if not obj or not getattr(obj, "pk", None):
        return "Save first to preview."

    raw_value = getattr(obj, field_name, "")
    image_src = resolve_image_src(raw_value)
    if not image_src:
        return "No image set."

    return format_html(
        (
            '<div style="display:flex; gap:16px; align-items:flex-start;">'
            '<img src="{}" alt="{}" style="width:120px; max-width:120px; border-radius:12px; '
            'border:1px solid rgba(255,255,255,0.12); object-fit:cover; background:#111;">'
            '<div style="min-width:0;">'
            '<div style="font-weight:700; margin-bottom:6px;">{}</div>'
            '<div style="font-size:12px; line-height:1.5; word-break:break-all; opacity:0.85;">{}</div>'
            "</div>"
            "</div>"
        ),
        image_src,
        label,
        label,
        raw_value,
    )
