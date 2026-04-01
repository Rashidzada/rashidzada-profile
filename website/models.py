from django.db import models
from django.urls import reverse


class SiteConfiguration(models.Model):
    site_name = models.CharField(max_length=100, default="Rashid Zada")
    full_name = models.CharField(max_length=150)
    headline = models.CharField(max_length=255)
    hero_intro = models.CharField(max_length=50, default="I'm")
    assistant_name = models.CharField(max_length=80, default="Snail Bot")
    assistant_greeting = models.TextField(
        default=(
            "Assalamualaikum. I am Snail Bot. Ask me about Rashid Zada's profile, "
            "skills, services, projects, experience, education, or contact details."
        )
    )
    about_heading = models.CharField(max_length=255)
    professional_summary = models.TextField()
    about_intro = models.TextField()
    about_body = models.TextField()
    footer_summary = models.TextField()
    career_objective = models.TextField()
    location = models.CharField(max_length=255)
    availability = models.CharField(max_length=255, blank=True)
    phone_display = models.CharField(max_length=50)
    phone_link = models.CharField(max_length=50)
    whatsapp_number = models.CharField(max_length=30)
    email = models.EmailField()
    portfolio_url = models.URLField()
    github_url = models.URLField()
    linkedin_url = models.URLField()
    typing_profile_url = models.URLField(blank=True)
    resume_document = models.CharField(max_length=255, blank=True, default="")
    profile_image = models.CharField(max_length=255, blank=True, default="")
    favicon_image = models.CharField(max_length=255, default="assets/img/favicon.png")
    apple_touch_icon = models.CharField(max_length=255, default="assets/img/apple-touch-icon.png")
    hero_background_image = models.CharField(max_length=255, default="assets/img/hero-bg.jpg")
    assistant_icon = models.CharField(max_length=255, default="assets/img/site/snail-bot.png")

    class Meta:
        verbose_name = "Site configuration"
        verbose_name_plural = "Site configuration"

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @property
    def whatsapp_url(self):
        return (
            f"https://wa.me/{self.whatsapp_number}"
            "?text=Assalamualaikum%2C%20I%20visited%20your%20website%20and%20want%20to%20contact%20you."
        )

    @property
    def phone_uri(self):
        return f"tel:{self.phone_link}"

    @property
    def initials(self):
        initials = [part[0].upper() for part in self.full_name.split() if part][:2]
        return "".join(initials) or self.site_name[:2].upper()

    @property
    def resume_view_url(self):
        from .file_utils import resolve_document_view_url

        return resolve_document_view_url(self.resume_document)

    @property
    def resume_download_url(self):
        from .file_utils import resolve_document_download_url

        return resolve_document_download_url(self.resume_document)


class PageIntro(models.Model):
    ABOUT = "about"
    RESUME = "resume"
    SERVICES = "services"
    PORTFOLIO = "portfolio"
    CONTACT = "contact"
    STARTER = "starter"
    PAGE_CHOICES = [
        (ABOUT, "About"),
        (RESUME, "Resume"),
        (SERVICES, "Services"),
        (PORTFOLIO, "Portfolio"),
        (CONTACT, "Contact"),
        (STARTER, "Starter"),
    ]

    page_key = models.CharField(max_length=20, choices=PAGE_CHOICES, unique=True)
    title = models.CharField(max_length=120)
    description = models.TextField()

    class Meta:
        ordering = ["page_key"]

    def __str__(self):
        return self.title


class SocialLink(models.Model):
    label = models.CharField(max_length=50)
    url = models.URLField()
    icon_class = models.CharField(max_length=50)
    order = models.PositiveSmallIntegerField(default=0)
    show_in_hero = models.BooleanField(default=True)
    show_in_footer = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.label


class TypedRole(models.Model):
    name = models.CharField(max_length=100)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


class AboutFact(models.Model):
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=255)
    link_url = models.URLField(blank=True)
    column = models.PositiveSmallIntegerField(default=1)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["column", "order", "id"]

    def __str__(self):
        return self.label


class Statistic(models.Model):
    label = models.CharField(max_length=100)
    value = models.PositiveIntegerField()
    suffix = models.CharField(max_length=10, blank=True)
    icon_class = models.CharField(max_length=50)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.label


class Skill(models.Model):
    name = models.CharField(max_length=100)
    proficiency = models.PositiveSmallIntegerField()
    column = models.PositiveSmallIntegerField(default=1)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["column", "order", "id"]

    def __str__(self):
        return self.name


class Certification(models.Model):
    title = models.CharField(max_length=150)
    icon_class = models.CharField(max_length=50)
    accent_color = models.CharField(max_length=20)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class Language(models.Model):
    name = models.CharField(max_length=50)
    proficiency = models.CharField(max_length=50)
    icon_class = models.CharField(max_length=50)
    accent_color = models.CharField(max_length=20)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.name} - {self.proficiency}"


class Strength(models.Model):
    title = models.CharField(max_length=150)
    icon_class = models.CharField(max_length=50)
    accent_color = models.CharField(max_length=20)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class ProfileHighlight(models.Model):
    title = models.CharField(max_length=150)
    subtitle = models.CharField(max_length=150)
    description = models.TextField()
    image_path = models.CharField(max_length=255, blank=True, default="")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class Education(models.Model):
    degree = models.CharField(max_length=150)
    start_year = models.PositiveSmallIntegerField()
    end_year = models.PositiveSmallIntegerField()
    institution = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.degree


class Experience(models.Model):
    role_title = models.CharField(max_length=150)
    organization = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    start_label = models.CharField(max_length=50)
    end_label = models.CharField(max_length=50)
    summary = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.role_title

    @property
    def period_label(self):
        return f"{self.start_label} - {self.end_label}"


class ExperienceBullet(models.Model):
    experience = models.ForeignKey(Experience, on_delete=models.CASCADE, related_name="bullets")
    text = models.TextField()
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.text[:80]


class Service(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    icon_class = models.CharField(max_length=50)
    short_description = models.TextField()
    summary_heading = models.CharField(max_length=150)
    summary_text = models.TextField()
    detail_heading = models.CharField(max_length=200)
    detail_intro = models.TextField()
    detail_body = models.TextField()
    detail_footer = models.TextField(blank=True)
    image_path = models.CharField(max_length=255, default="assets/img/services/services-4.webp")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("service-detail", kwargs={"slug": self.slug})


class ServiceBullet(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="bullets")
    text = models.TextField()
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.text[:80]


class ProjectCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name_plural = "Project categories"

    def __str__(self):
        return self.name

    @property
    def filter_class(self):
        return f"filter-{self.slug}"


class Project(models.Model):
    category = models.ForeignKey(ProjectCategory, on_delete=models.PROTECT, related_name="projects")
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    summary = models.TextField()
    client = models.CharField(max_length=150, blank=True)
    project_date_label = models.CharField(max_length=100, blank=True)
    project_url = models.URLField(blank=True)
    detail_heading = models.CharField(max_length=200)
    description = models.TextField()
    card_image = models.CharField(max_length=255)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("portfolio-detail", kwargs={"slug": self.slug})


class ProjectHighlight(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="highlights")
    text = models.TextField()
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.text[:80]


class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="images")
    image_path = models.CharField(max_length=255)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.image_path
