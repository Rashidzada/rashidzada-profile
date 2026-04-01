from website.image_utils import resolve_image_src
from website.models import (
    AboutFact,
    Certification,
    Education,
    Experience,
    Language,
    PageIntro,
    ProfileHighlight,
    Project,
    ProjectCategory,
    Service,
    SiteConfiguration,
    Skill,
    SocialLink,
    Statistic,
    Strength,
    TypedRole,
)


def image_payload(value):
    return {
        "path": value or "",
        "url": resolve_image_src(value),
    }


def serialize_site(site):
    return {
        "site_name": site.site_name,
        "full_name": site.full_name,
        "headline": site.headline,
        "hero_intro": site.hero_intro,
        "assistant_name": site.assistant_name,
        "assistant_greeting": site.assistant_greeting,
        "about_heading": site.about_heading,
        "professional_summary": site.professional_summary,
        "about_intro": site.about_intro,
        "about_body": site.about_body,
        "footer_summary": site.footer_summary,
        "career_objective": site.career_objective,
        "location": site.location,
        "availability": site.availability,
        "phone_display": site.phone_display,
        "phone_link": site.phone_link,
        "phone_uri": site.phone_uri,
        "whatsapp_number": site.whatsapp_number,
        "whatsapp_url": site.whatsapp_url,
        "email": site.email,
        "portfolio_url": site.portfolio_url,
        "github_url": site.github_url,
        "linkedin_url": site.linkedin_url,
        "typing_profile_url": site.typing_profile_url,
        "profile_image": image_payload(site.profile_image),
        "favicon_image": image_payload(site.favicon_image),
        "apple_touch_icon": image_payload(site.apple_touch_icon),
        "hero_background_image": image_payload(site.hero_background_image),
        "assistant_icon": image_payload(site.assistant_icon),
    }


def serialize_page_intro(page_intro):
    return {
        "page_key": page_intro.page_key,
        "title": page_intro.title,
        "description": page_intro.description,
    }


def serialize_social_link(social_link):
    return {
        "label": social_link.label,
        "url": social_link.url,
        "icon_class": social_link.icon_class,
        "order": social_link.order,
        "show_in_hero": social_link.show_in_hero,
        "show_in_footer": social_link.show_in_footer,
    }


def serialize_typed_role(role):
    return {
        "name": role.name,
        "order": role.order,
    }


def serialize_about_fact(fact):
    return {
        "label": fact.label,
        "value": fact.value,
        "link_url": fact.link_url,
        "column": fact.column,
        "order": fact.order,
    }


def serialize_statistic(statistic):
    return {
        "label": statistic.label,
        "value": statistic.value,
        "suffix": statistic.suffix,
        "icon_class": statistic.icon_class,
        "order": statistic.order,
    }


def serialize_skill(skill):
    return {
        "name": skill.name,
        "proficiency": skill.proficiency,
        "column": skill.column,
        "order": skill.order,
    }


def serialize_certification(certification):
    return {
        "title": certification.title,
        "icon_class": certification.icon_class,
        "accent_color": certification.accent_color,
        "order": certification.order,
    }


def serialize_language(language):
    return {
        "name": language.name,
        "proficiency": language.proficiency,
        "icon_class": language.icon_class,
        "accent_color": language.accent_color,
        "order": language.order,
    }


def serialize_strength(strength):
    return {
        "title": strength.title,
        "icon_class": strength.icon_class,
        "accent_color": strength.accent_color,
        "order": strength.order,
    }


def serialize_profile_highlight(highlight):
    return {
        "title": highlight.title,
        "subtitle": highlight.subtitle,
        "description": highlight.description,
        "image": image_payload(highlight.image_path),
        "order": highlight.order,
    }


def serialize_education(education):
    return {
        "degree": education.degree,
        "start_year": education.start_year,
        "end_year": education.end_year,
        "institution": education.institution,
        "description": education.description,
        "order": education.order,
    }


def serialize_experience(experience):
    return {
        "role_title": experience.role_title,
        "organization": experience.organization,
        "location": experience.location,
        "start_label": experience.start_label,
        "end_label": experience.end_label,
        "period_label": experience.period_label,
        "summary": experience.summary,
        "order": experience.order,
        "bullets": [
            {
                "text": bullet.text,
                "order": bullet.order,
            }
            for bullet in experience.bullets.all()
        ],
    }


def serialize_service(service):
    return {
        "title": service.title,
        "slug": service.slug,
        "icon_class": service.icon_class,
        "short_description": service.short_description,
        "summary_heading": service.summary_heading,
        "summary_text": service.summary_text,
        "detail_heading": service.detail_heading,
        "detail_intro": service.detail_intro,
        "detail_body": service.detail_body,
        "detail_footer": service.detail_footer,
        "order": service.order,
        "absolute_url": service.get_absolute_url(),
        "image": image_payload(service.image_path),
        "bullets": [
            {
                "text": bullet.text,
                "order": bullet.order,
            }
            for bullet in service.bullets.all()
        ],
    }


def serialize_project_category(category):
    return {
        "name": category.name,
        "slug": category.slug,
        "order": category.order,
        "filter_class": category.filter_class,
    }


def serialize_project(project):
    return {
        "title": project.title,
        "slug": project.slug,
        "summary": project.summary,
        "client": project.client,
        "project_date_label": project.project_date_label,
        "project_url": project.project_url,
        "detail_heading": project.detail_heading,
        "description": project.description,
        "order": project.order,
        "absolute_url": project.get_absolute_url(),
        "category": serialize_project_category(project.category),
        "card_image": image_payload(project.card_image),
        "highlights": [
            {
                "text": highlight.text,
                "order": highlight.order,
            }
            for highlight in project.highlights.all()
        ],
        "images": [
            {
                "image": image_payload(image.image_path),
                "order": image.order,
            }
            for image in project.images.all()
        ],
    }


def build_profile_payload():
    site = SiteConfiguration.objects.first()
    return {
        "site": serialize_site(site) if site else {},
        "page_intros": [serialize_page_intro(item) for item in PageIntro.objects.all()],
        "social_links": [serialize_social_link(item) for item in SocialLink.objects.all()],
        "typed_roles": [serialize_typed_role(item) for item in TypedRole.objects.all()],
        "about_facts": [serialize_about_fact(item) for item in AboutFact.objects.all()],
        "statistics": [serialize_statistic(item) for item in Statistic.objects.all()],
        "skills": [serialize_skill(item) for item in Skill.objects.all()],
        "certifications": [serialize_certification(item) for item in Certification.objects.all()],
        "languages": [serialize_language(item) for item in Language.objects.all()],
        "strengths": [serialize_strength(item) for item in Strength.objects.all()],
        "profile_highlights": [serialize_profile_highlight(item) for item in ProfileHighlight.objects.all()],
        "education": [serialize_education(item) for item in Education.objects.all()],
        "experiences": [
            serialize_experience(item)
            for item in Experience.objects.prefetch_related("bullets")
        ],
        "services": [
            serialize_service(item)
            for item in Service.objects.prefetch_related("bullets")
        ],
        "project_categories": [
            serialize_project_category(item)
            for item in ProjectCategory.objects.all()
        ],
        "projects": [
            serialize_project(item)
            for item in Project.objects.select_related("category").prefetch_related("highlights", "images")
        ],
    }
