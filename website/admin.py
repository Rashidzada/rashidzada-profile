from django.contrib import admin

from .admin_image_tools import build_image_admin_form, render_admin_image_preview
from .models import (
    AboutFact,
    Certification,
    Education,
    Experience,
    ExperienceBullet,
    Language,
    PageIntro,
    ProfileHighlight,
    Project,
    ProjectCategory,
    ProjectHighlight,
    ProjectImage,
    Service,
    ServiceBullet,
    SiteConfiguration,
    Skill,
    SocialLink,
    Statistic,
    Strength,
    TypedRole,
)

admin.site.site_header = "Rashid Zada Profile"
admin.site.site_title = "Profile Admin"
admin.site.index_title = "Manage profile content"
admin.site.empty_value_display = "Not set"


def preview_display(field_name, label):
    @admin.display(description=f"{label} preview")
    def _preview(self, obj):
        return render_admin_image_preview(obj, field_name, label)

    return _preview


SiteConfigurationAdminForm = build_image_admin_form(
    SiteConfiguration,
    {
        "profile_image": {"label": "Profile image", "folder": "site/profile"},
        "favicon_image": {"label": "Favicon image", "folder": "site/favicon"},
        "apple_touch_icon": {"label": "Apple touch icon", "folder": "site/apple-touch"},
        "hero_background_image": {"label": "Hero background image", "folder": "site/hero"},
    },
)
ProfileHighlightAdminForm = build_image_admin_form(
    ProfileHighlight,
    {
        "image_path": {"label": "Highlight image", "folder": "profile-highlights"},
    },
)
ServiceAdminForm = build_image_admin_form(
    Service,
    {
        "image_path": {"label": "Service image", "folder": "services"},
    },
)
ProjectAdminForm = build_image_admin_form(
    Project,
    {
        "card_image": {"label": "Project card image", "folder": "projects/cards"},
    },
)
ProjectImageInlineForm = build_image_admin_form(
    ProjectImage,
    {
        "image_path": {"label": "Gallery image", "folder": "projects/gallery"},
    },
)


class ExperienceBulletInline(admin.TabularInline):
    model = ExperienceBullet
    extra = 1


class ServiceBulletInline(admin.TabularInline):
    model = ServiceBullet
    extra = 1


class ProjectHighlightInline(admin.TabularInline):
    model = ProjectHighlight
    extra = 1


class ProjectImageInline(admin.StackedInline):
    model = ProjectImage
    form = ProjectImageInlineForm
    extra = 1
    fields = ("image_preview", ("image_path_upload", "image_path_url_input", "image_path_clear"), "order")
    readonly_fields = ("image_preview",)

    image_preview = preview_display("image_path", "Gallery image")


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    form = SiteConfigurationAdminForm
    list_display = ("full_name", "headline", "email", "phone_display", "profile_image", "favicon_image")
    readonly_fields = (
        "profile_image_preview",
        "favicon_image_preview",
        "apple_touch_icon_preview",
        "hero_background_image_preview",
    )
    fieldsets = (
        (
            "Identity",
            {
                "fields": (
                    ("site_name", "full_name"),
                    "headline",
                    ("hero_intro", "about_heading"),
                )
            },
        ),
        (
            "Profile Content",
            {
                "fields": (
                    "professional_summary",
                    "about_intro",
                    "about_body",
                    "footer_summary",
                    "career_objective",
                )
            },
        ),
        (
            "Contact & Links",
            {
                "fields": (
                    ("location", "availability"),
                    ("phone_display", "phone_link"),
                    ("whatsapp_number", "email"),
                    "portfolio_url",
                    "github_url",
                    "linkedin_url",
                    "typing_profile_url",
                )
            },
        ),
        (
            "Image Sources",
            {
                "description": "Use either upload or URL for each image. Public Google Drive links are supported.",
                "fields": (
                    "profile_image_preview",
                    ("profile_image_upload", "profile_image_url_input", "profile_image_clear"),
                    "favicon_image_preview",
                    ("favicon_image_upload", "favicon_image_url_input", "favicon_image_clear"),
                    "apple_touch_icon_preview",
                    ("apple_touch_icon_upload", "apple_touch_icon_url_input", "apple_touch_icon_clear"),
                    "hero_background_image_preview",
                    ("hero_background_image_upload", "hero_background_image_url_input", "hero_background_image_clear"),
                ),
            },
        ),
    )

    profile_image_preview = preview_display("profile_image", "Profile image")
    favicon_image_preview = preview_display("favicon_image", "Favicon image")
    apple_touch_icon_preview = preview_display("apple_touch_icon", "Apple touch icon")
    hero_background_image_preview = preview_display("hero_background_image", "Hero background image")


@admin.register(PageIntro)
class PageIntroAdmin(admin.ModelAdmin):
    list_display = ("page_key", "title")


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ("label", "url", "order", "show_in_hero", "show_in_footer")
    list_editable = ("order", "show_in_hero", "show_in_footer")


@admin.register(TypedRole)
class TypedRoleAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    list_editable = ("order",)


@admin.register(AboutFact)
class AboutFactAdmin(admin.ModelAdmin):
    list_display = ("label", "value", "column", "order")
    list_editable = ("column", "order")


@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    list_display = ("label", "value", "suffix", "icon_class", "order")
    list_editable = ("order",)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "proficiency", "column", "order")
    list_editable = ("proficiency", "column", "order")


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ("title", "order")
    list_editable = ("order",)


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("name", "proficiency", "order")
    list_editable = ("proficiency", "order")


@admin.register(Strength)
class StrengthAdmin(admin.ModelAdmin):
    list_display = ("title", "order")
    list_editable = ("order",)


@admin.register(ProfileHighlight)
class ProfileHighlightAdmin(admin.ModelAdmin):
    form = ProfileHighlightAdminForm
    list_display = ("title", "subtitle", "order")
    list_editable = ("order",)
    fields = ("title", "subtitle", "description", "image_preview", ("image_path_upload", "image_path_url_input", "image_path_clear"), "order")
    readonly_fields = ("image_preview",)

    image_preview = preview_display("image_path", "Highlight image")


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ("degree", "institution", "start_year", "end_year", "order")
    list_editable = ("order",)


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("role_title", "organization", "start_label", "end_label", "order")
    list_editable = ("order",)
    inlines = [ExperienceBulletInline]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    form = ServiceAdminForm
    list_display = ("title", "slug", "order")
    list_editable = ("order",)
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ServiceBulletInline]
    readonly_fields = ("image_preview",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("title", "slug"),
                    ("icon_class", "order"),
                    "short_description",
                    "summary_heading",
                    "summary_text",
                    "detail_heading",
                    "detail_intro",
                    "detail_body",
                    "detail_footer",
                )
            },
        ),
        (
            "Image Source",
            {
                "description": "Upload a service image or paste a public/Google Drive image URL.",
                "fields": (
                    "image_preview",
                    ("image_path_upload", "image_path_url_input", "image_path_clear"),
                ),
            },
        ),
    )

    image_preview = preview_display("image_path", "Service image")


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order")
    list_editable = ("order",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
    list_display = ("title", "category", "slug", "order")
    list_editable = ("order",)
    list_filter = ("category",)
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProjectHighlightInline, ProjectImageInline]
    readonly_fields = ("card_image_preview",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("title", "slug"),
                    ("category", "order"),
                    "summary",
                    ("client", "project_date_label"),
                    "project_url",
                    "detail_heading",
                    "description",
                )
            },
        ),
        (
            "Card Image",
            {
                "description": "Upload a project card image or paste a public/Google Drive image URL.",
                "fields": (
                    "card_image_preview",
                    ("card_image_upload", "card_image_url_input", "card_image_clear"),
                ),
            },
        ),
    )

    card_image_preview = preview_display("card_image", "Project card image")
