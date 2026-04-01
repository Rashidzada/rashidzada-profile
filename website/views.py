import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods, require_POST

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
    SiteConfiguration,
    Skill,
    SocialLink,
    Statistic,
    Strength,
    TypedRole,
)
from .profile_api import (
    build_profile_payload,
    serialize_about_fact,
    serialize_certification,
    serialize_education,
    serialize_experience,
    serialize_language,
    serialize_page_intro,
    serialize_profile_highlight,
    serialize_project,
    serialize_project_category,
    serialize_service,
    serialize_site,
    serialize_skill,
    serialize_social_link,
    serialize_statistic,
    serialize_strength,
    serialize_typed_role,
)
from .snail_bot import get_snail_bot_reply


def api_success(data, status=200, **extra):
    payload = {"ok": True, "data": data}
    payload.update(extra)
    return JsonResponse(payload, status=status)


def api_error(message, status=400):
    return JsonResponse({"ok": False, "error": message}, status=status)


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


@require_GET
def profile_api(request):
    return api_success(build_profile_payload())


@require_GET
def site_configuration_api(request):
    site = get_object_or_404(SiteConfiguration, pk=1)
    return api_success(serialize_site(site))


@require_GET
def page_intro_list_api(request):
    data = [serialize_page_intro(item) for item in PageIntro.objects.all()]
    return api_success(data, count=len(data))


@require_GET
def social_link_list_api(request):
    data = [serialize_social_link(item) for item in SocialLink.objects.all()]
    return api_success(data, count=len(data))


@require_GET
def typed_role_list_api(request):
    data = [serialize_typed_role(item) for item in TypedRole.objects.all()]
    return api_success(data, count=len(data))


@require_GET
def about_fact_list_api(request):
    data = [serialize_about_fact(item) for item in AboutFact.objects.all()]
    return api_success(data, count=len(data))


@require_GET
def statistic_list_api(request):
    data = [serialize_statistic(item) for item in Statistic.objects.all()]
    return api_success(data, count=len(data))


@require_GET
def skill_list_api(request):
    data = [serialize_skill(item) for item in Skill.objects.all()]
    return api_success(data, count=len(data))


@require_GET
def certification_list_api(request):
    data = [serialize_certification(item) for item in Certification.objects.all()]
    return api_success(data, count=len(data))


@require_GET
def language_list_api(request):
    data = [serialize_language(item) for item in Language.objects.all()]
    return api_success(data, count=len(data))


@require_GET
def strength_list_api(request):
    data = [serialize_strength(item) for item in Strength.objects.all()]
    return api_success(data, count=len(data))


@require_GET
def profile_highlight_list_api(request):
    data = [serialize_profile_highlight(item) for item in ProfileHighlight.objects.all()]
    return api_success(data, count=len(data))


@require_GET
def education_list_api(request):
    data = [serialize_education(item) for item in Education.objects.all()]
    return api_success(data, count=len(data))


@require_GET
def experience_list_api(request):
    data = [
        serialize_experience(item)
        for item in Experience.objects.prefetch_related("bullets")
    ]
    return api_success(data, count=len(data))


@require_GET
def service_list_api(request):
    data = [
        serialize_service(item)
        for item in Service.objects.prefetch_related("bullets")
    ]
    return api_success(data, count=len(data))


@require_GET
def service_detail_api(request, slug):
    service = get_object_or_404(Service.objects.prefetch_related("bullets"), slug=slug)
    return api_success(serialize_service(service))


@require_GET
def project_category_list_api(request):
    data = [serialize_project_category(item) for item in ProjectCategory.objects.all()]
    return api_success(data, count=len(data))


@require_GET
def project_list_api(request):
    data = [
        serialize_project(item)
        for item in Project.objects.select_related("category").prefetch_related("highlights", "images")
    ]
    return api_success(data, count=len(data))


@require_GET
def project_detail_api(request, slug):
    project = get_object_or_404(
        Project.objects.select_related("category").prefetch_related("highlights", "images"),
        slug=slug,
    )
    return api_success(serialize_project(project))


@csrf_exempt
@require_http_methods(["POST"])
def snail_bot_chat_api(request):
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        payload = {}

    message = (payload.get("message") or request.POST.get("message") or "").strip()
    response = get_snail_bot_reply(message)
    return api_success(response)


@csrf_exempt
@require_POST
def contact_form(request):
    return HttpResponse("OK", content_type="text/plain")
