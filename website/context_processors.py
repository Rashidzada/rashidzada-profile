from .models import SiteConfiguration, SocialLink


def site_defaults(request):
    site = SiteConfiguration.objects.first()
    social_links = SocialLink.objects.order_by("order")
    return {
        "site": site,
        "hero_social_links": social_links.filter(show_in_hero=True),
        "footer_social_links": social_links.filter(show_in_footer=True),
    }
