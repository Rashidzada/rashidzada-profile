import json

from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import Project, Service, SiteConfiguration


class PageRoutingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_portfolio")
        cls.site = SiteConfiguration.objects.get(pk=1)
        cls.first_service = Service.objects.order_by("order", "id").first()
        cls.first_project = Project.objects.order_by("order", "id").first()

    def setUp(self):
        self.client = Client()

    def test_named_pages_render(self):
        urls = [
            reverse("home"),
            reverse("about"),
            reverse("resume"),
            reverse("services"),
            reverse("service-detail", kwargs={"slug": self.first_service.slug}),
            reverse("portfolio"),
            reverse("portfolio-detail", kwargs={"slug": self.first_project.slug}),
            reverse("contact"),
            reverse("starter-page"),
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_seeded_home_page_uses_real_content(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, self.site.full_name)
        self.assertContains(response, "Full Stack Developer")
        self.assertContains(response, self.site.favicon_image)
        self.assertContains(response, "Snail Bot")

    def test_about_page_avoids_old_placeholder_people_images(self):
        response = self.client.get(reverse("about"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "assets/img/person/")

    def test_contact_form_endpoint_returns_ok(self):
        response = self.client.post(
            reverse("contact-form"),
            {
                "name": "Test User",
                "email": "test@example.com",
                "subject": "Test",
                "message": "Hello",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"OK")

    def test_legacy_html_urls_redirect_to_clean_routes(self):
        redirects = {
            "/index.html": reverse("home"),
            "/about.html": reverse("about"),
            "/resume.html": reverse("resume"),
            "/services.html": reverse("services"),
            "/portfolio.html": reverse("portfolio"),
            "/contact.html": reverse("contact"),
            "/starter-page.html": reverse("starter-page"),
        }

        for legacy_url, clean_url in redirects.items():
            with self.subTest(legacy_url=legacy_url):
                response = self.client.get(legacy_url)
                self.assertRedirects(response, clean_url, status_code=301)

    def test_legacy_detail_urls_redirect_to_first_seeded_object(self):
        response = self.client.get("/service-details.html")
        self.assertRedirects(response, reverse("service-detail", kwargs={"slug": self.first_service.slug}), status_code=302)

        response = self.client.get("/portfolio-details.html")
        self.assertRedirects(response, reverse("portfolio-detail", kwargs={"slug": self.first_project.slug}), status_code=302)

    def test_admin_login_uses_profile_branding(self):
        response = self.client.get("/admin/login/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rashid Zada Profile")
        self.assertNotContains(response, "Django administration")

    def test_admin_index_uses_profile_branding(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            username="brandadmin",
            email="brandadmin@example.com",
            password="StrongPass123!",
        )
        self.client.force_login(admin_user)

        response = self.client.get("/admin/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Manage profile content")
        self.assertContains(response, "Profile")
        self.assertNotContains(response, "Django administration")

    def test_site_configuration_admin_shows_upload_and_url_fields(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            username="mediaadmin",
            email="mediaadmin@example.com",
            password="StrongPass123!",
        )
        self.client.force_login(admin_user)

        response = self.client.get("/admin/website/siteconfiguration/1/change/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Profile image upload")
        self.assertContains(response, "Profile image URL")
        self.assertContains(response, "Resume document upload")
        self.assertContains(response, "Resume document URL")
        self.assertContains(response, "Google Drive")

    def test_resume_page_shows_cv_actions_when_resume_is_configured(self):
        self.site.resume_document = "https://example.com/rashid-zada-cv.pdf"
        self.site.save()

        response = self.client.get(reverse("resume"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "View CV")
        self.assertContains(response, "bi bi-download")
        self.assertContains(response, "https://example.com/rashid-zada-cv.pdf")

    def test_profile_api_returns_seeded_content(self):
        response = self.client.get(reverse("api-profile"))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["data"]["site"]["full_name"], "Rashid Zada")
        self.assertEqual(payload["data"]["site"]["assistant_name"], "Snail Bot")
        self.assertIn("resume_document", payload["data"]["site"])
        self.assertGreaterEqual(len(payload["data"]["services"]), 1)

    def test_service_detail_api_returns_requested_service(self):
        response = self.client.get(
            reverse("api-service-detail", kwargs={"slug": self.first_service.slug})
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["data"]["slug"], self.first_service.slug)

    def test_snail_bot_rejects_unrelated_questions(self):
        response = self.client.post(
            reverse("api-snail-bot-chat"),
            data='{"message":"What is the weather today?"}',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["data"]["related"])
        self.assertIn("only answer questions about Rashid Zada", payload["data"]["message"])

    def test_snail_bot_answers_profile_questions_without_provider_key(self):
        response = self.client.post(
            reverse("api-snail-bot-chat"),
            data='{"message":"What services does Rashid offer?"}',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["data"]["related"])
        self.assertIn(payload["data"]["mode"], {"local", "deepseek"})
        self.assertIn("services", payload["data"]["message"].lower())

    def test_snail_bot_stream_endpoint_streams_tokens(self):
        response = self.client.post(
            reverse("api-snail-bot-stream"),
            data='{"message":"What services does Rashid offer?"}',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        body = b"".join(response.streaming_content).decode("utf-8").strip().splitlines()
        events = [json.loads(line) for line in body if line.strip()]

        self.assertTrue(events)
        self.assertEqual(events[0]["type"], "meta")
        self.assertIn(events[0]["mode"], {"local", "deepseek"})
        self.assertEqual(events[-1]["type"], "done")
        self.assertTrue(any(event["type"] == "token" for event in events))


class SuperuserCommandTests(TestCase):
    def test_ensure_superuser_creates_user_from_arguments(self):
        User = get_user_model()

        call_command(
            "ensure_superuser",
            username="admin",
            email="admin@example.com",
            password="StrongPass123!",
        )

        self.assertTrue(User.objects.filter(username="admin", is_superuser=True).exists())

    def test_ensure_superuser_is_idempotent(self):
        User = get_user_model()

        call_command(
            "ensure_superuser",
            username="admin",
            email="admin@example.com",
            password="StrongPass123!",
        )
        call_command(
            "ensure_superuser",
            username="admin",
            email="admin@example.com",
            password="StrongPass123!",
        )

        self.assertEqual(User.objects.filter(username="admin").count(), 1)
