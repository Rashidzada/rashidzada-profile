from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import (
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
    Skill,
    Statistic,
    Strength,
    TypedRole,
)


def build_page_context(active_page, page_key=None, **extra):
    context = {"active_page": active_page}
    if page_key:
        context["page_intro"] = PageIntro.objects.filter(page_key=page_key).first()
    context.update(extra)
    return context


def build_feature_cards():
    cards = []
    cards.extend(
        {
            "title": certification.title,
            "icon_class": certification.icon_class,
            "accent_color": certification.accent_color,
        }
        for certification in Certification.objects.all()
    )
    cards.extend(
        {
            "title": f"{language.name} - {language.proficiency}",
            "icon_class": language.icon_class,
            "accent_color": language.accent_color,
        }
        for language in Language.objects.all()
    )
    cards.extend(
        {
            "title": strength.title,
            "icon_class": strength.icon_class,
            "accent_color": strength.accent_color,
        }
        for strength in Strength.objects.all()
    )
    return cards


def home(request):
    return render(
        request,
        "personal/index.html",
        build_page_context(
            "home",
            typed_roles=TypedRole.objects.all(),
        ),
    )


def about(request):
    facts = AboutFact.objects.all()
    return render(
        request,
        "personal/about.html",
        build_page_context(
            "about",
            PageIntro.ABOUT,
            about_facts_col_1=facts.filter(column=1),
            about_facts_col_2=facts.filter(column=2),
            stats=Statistic.objects.all(),
            skills_col_1=Skill.objects.filter(column=1),
            skills_col_2=Skill.objects.filter(column=2),
            feature_cards=build_feature_cards(),
            profile_highlights=ProfileHighlight.objects.all(),
        ),
    )


def resume(request):
    return render(
        request,
        "personal/resume.html",
        build_page_context(
            "resume",
            PageIntro.RESUME,
            education_items=Education.objects.all(),
            experience_items=Experience.objects.prefetch_related("bullets"),
        ),
    )


def services(request):
    return render(
        request,
        "personal/services.html",
        build_page_context(
            "services",
            PageIntro.SERVICES,
            services_list=Service.objects.all(),
        ),
    )


def service_detail(request, slug):
    selected_service = get_object_or_404(Service.objects.prefetch_related("bullets"), slug=slug)
    return render(
        request,
        "personal/service-details.html",
        build_page_context(
            "services",
            selected_service=selected_service,
            services_list=Service.objects.all(),
        ),
    )


def service_detail_landing(request):
    first_service = Service.objects.order_by("order", "id").first()
    if first_service is None:
        return redirect("services")
    return redirect(first_service.get_absolute_url())


def portfolio(request):
    return render(
        request,
        "personal/portfolio.html",
        build_page_context(
            "portfolio",
            PageIntro.PORTFOLIO,
            project_categories=ProjectCategory.objects.all(),
            projects=Project.objects.select_related("category"),
        ),
    )


def portfolio_detail(request, slug):
    selected_project = get_object_or_404(
        Project.objects.select_related("category").prefetch_related("images", "highlights"),
        slug=slug,
    )
    return render(
        request,
        "personal/portfolio-details.html",
        build_page_context(
            "portfolio",
            selected_project=selected_project,
        ),
    )


def portfolio_detail_landing(request):
    first_project = Project.objects.order_by("order", "id").first()
    if first_project is None:
        return redirect("portfolio")
    return redirect(first_project.get_absolute_url())


def contact(request):
    return render(
        request,
        "personal/contact.html",
        build_page_context("contact", PageIntro.CONTACT),
    )


def starter_page(request):
    return render(
        request,
        "personal/starter-page.html",
        build_page_context(
            "starter",
            PageIntro.STARTER,
            certifications=Certification.objects.all(),
            languages=Language.objects.all(),
            strengths=Strength.objects.all(),
        ),
    )


@csrf_exempt
@require_POST
def contact_form(request):
    return HttpResponse("OK", content_type="text/plain")
