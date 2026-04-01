from django.urls import path
from django.views.generic import RedirectView

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("resume/", views.resume, name="resume"),
    path("services/", views.services, name="services"),
    path("services/details/", views.service_detail_landing, name="service-detail-landing"),
    path("services/<slug:slug>/", views.service_detail, name="service-detail"),
    path("portfolio/", views.portfolio, name="portfolio"),
    path("portfolio/details/", views.portfolio_detail_landing, name="portfolio-detail-landing"),
    path("portfolio/<slug:slug>/", views.portfolio_detail, name="portfolio-detail"),
    path("contact/", views.contact, name="contact"),
    path("contact/submit/", views.contact_form, name="contact-form"),
    path("starter-page/", views.starter_page, name="starter-page"),
    path("index.html", RedirectView.as_view(pattern_name="home", permanent=True)),
    path("about.html", RedirectView.as_view(pattern_name="about", permanent=True)),
    path("resume.html", RedirectView.as_view(pattern_name="resume", permanent=True)),
    path("services.html", RedirectView.as_view(pattern_name="services", permanent=True)),
    path("service-details.html", views.service_detail_landing, name="legacy-service-detail"),
    path("portfolio.html", RedirectView.as_view(pattern_name="portfolio", permanent=True)),
    path("portfolio-details.html", views.portfolio_detail_landing, name="legacy-portfolio-detail"),
    path("contact.html", RedirectView.as_view(pattern_name="contact", permanent=True)),
    path("starter-page.html", RedirectView.as_view(pattern_name="starter-page", permanent=True)),
    path("forms/contact.php", views.contact_form, name="legacy-contact-form"),
]
