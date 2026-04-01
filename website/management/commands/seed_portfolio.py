import os
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

from website.models import (
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


BASE_DIR = Path(__file__).resolve().parents[3]
SITE_IMAGE_DIR = BASE_DIR / "static" / "assets" / "img" / "site"
DEFAULT_PROFILE_IMAGE = ""
DEFAULT_FAVICON_IMAGE = "assets/img/favicon.png"
DEFAULT_APPLE_TOUCH_ICON = "assets/img/apple-touch-icon.png"
DEFAULT_HERO_BACKGROUND_IMAGE = "assets/img/hero-bg.jpg"
IMAGE_RESAMPLING = getattr(Image, "Resampling", Image).LANCZOS


class Command(BaseCommand):
    help = "Seed the portfolio database with Rashid Zada CV data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--profile-source",
            dest="profile_source",
            help="Absolute path to a profile photo to import into the portfolio static assets.",
        )

    def build_circle_mask(self, size):
        mask = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size - 1, size - 1), fill=255)
        return mask

    def build_avatar_image(self, rgba_image, size, centering=(0.5, 0.38)):
        avatar_image = ImageOps.fit(
            rgba_image,
            (size, size),
            method=IMAGE_RESAMPLING,
            centering=centering,
        )
        avatar_image.putalpha(self.build_circle_mask(size))
        return avatar_image

    def build_favicon_image(self, rgba_image):
        return ImageOps.fit(
            rgba_image.convert("RGB"),
            (512, 512),
            method=IMAGE_RESAMPLING,
            centering=(0.5, 0.34),
        )

    def build_hero_background(self, rgb_image):
        hero_size = (1920, 1080)
        base_background = ImageOps.fit(
            rgb_image,
            hero_size,
            method=IMAGE_RESAMPLING,
            centering=(0.58, 0.34),
        )
        base_background = base_background.filter(ImageFilter.GaussianBlur(22))
        base_background = ImageEnhance.Color(base_background).enhance(0.38)
        base_background = ImageEnhance.Brightness(base_background).enhance(0.4)

        hero_image = base_background.convert("RGBA")

        dark_overlay = Image.new("RGBA", hero_size, (0, 0, 0, 0))
        dark_overlay_draw = ImageDraw.Draw(dark_overlay)
        for x in range(hero_size[0]):
            alpha = int(235 - ((x / hero_size[0]) * 170))
            dark_overlay_draw.line(
                ((x, 0), (x, hero_size[1])),
                fill=(4, 7, 10, max(50, alpha)),
            )
        hero_image.alpha_composite(dark_overlay)

        accent_glow = Image.new("RGBA", hero_size, (0, 0, 0, 0))
        accent_draw = ImageDraw.Draw(accent_glow)
        accent_draw.ellipse((-280, 520, 760, 1500), fill=(24, 210, 110, 48))
        accent_draw.ellipse((1120, -120, 1960, 760), fill=(35, 121, 255, 54))
        accent_glow = accent_glow.filter(ImageFilter.GaussianBlur(130))
        hero_image.alpha_composite(accent_glow)

        return hero_image.convert("RGB")

    def build_site_image_assets(self, profile_source):
        resolved_source = (profile_source or os.getenv("PORTFOLIO_PROFILE_SOURCE", "")).strip()
        image_paths = {
            "profile_image": DEFAULT_PROFILE_IMAGE,
            "favicon_image": DEFAULT_FAVICON_IMAGE,
            "apple_touch_icon": DEFAULT_APPLE_TOUCH_ICON,
            "hero_background_image": DEFAULT_HERO_BACKGROUND_IMAGE,
            "has_custom_profile": False,
        }

        if not resolved_source:
            return image_paths

        source_path = Path(resolved_source).expanduser()
        if not source_path.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"Profile image source not found: {source_path}. Keeping default static images."
                )
            )
            return image_paths

        SITE_IMAGE_DIR.mkdir(parents=True, exist_ok=True)

        with Image.open(source_path) as source_image:
            normalized_image = ImageOps.exif_transpose(source_image)
            rgba_image = normalized_image.convert("RGBA")
            rgb_image = Image.new("RGB", rgba_image.size, "white")
            rgb_image.paste(rgba_image, mask=rgba_image.getchannel("A"))

            if max(rgb_image.size) > 1400:
                rgb_image.thumbnail((1400, 1400), IMAGE_RESAMPLING)
                rgba_image = rgb_image.convert("RGBA")

            avatar_image = self.build_avatar_image(rgba_image, 720)
            profile_target = SITE_IMAGE_DIR / "profile-avatar.png"
            avatar_image.save(profile_target, format="PNG", optimize=True)

            favicon_image = self.build_favicon_image(rgba_image)

            favicon_target = SITE_IMAGE_DIR / "favicon.png"
            favicon_image.resize((64, 64), IMAGE_RESAMPLING).save(
                favicon_target,
                format="PNG",
                optimize=True,
            )

            apple_touch_target = SITE_IMAGE_DIR / "apple-touch-icon.png"
            favicon_image.resize((180, 180), IMAGE_RESAMPLING).save(
                apple_touch_target,
                format="PNG",
                optimize=True,
            )

            hero_background_target = SITE_IMAGE_DIR / "hero-background.jpg"
            self.build_hero_background(rgb_image).save(
                hero_background_target,
                format="JPEG",
                quality=90,
                optimize=True,
            )

        self.stdout.write(
            self.style.SUCCESS(f"Imported custom profile photo from {source_path}.")
        )
        return {
            "profile_image": "assets/img/site/profile-avatar.png",
            "favicon_image": "assets/img/site/favicon.png",
            "apple_touch_icon": "assets/img/site/apple-touch-icon.png",
            "hero_background_image": "assets/img/site/hero-background.jpg",
            "has_custom_profile": True,
        }

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Resetting portfolio content...")
        ProjectImage.objects.all().delete()
        ProjectHighlight.objects.all().delete()
        Project.objects.all().delete()
        ProjectCategory.objects.all().delete()
        ServiceBullet.objects.all().delete()
        Service.objects.all().delete()
        ExperienceBullet.objects.all().delete()
        Experience.objects.all().delete()
        Education.objects.all().delete()
        ProfileHighlight.objects.all().delete()
        Strength.objects.all().delete()
        Language.objects.all().delete()
        Certification.objects.all().delete()
        Skill.objects.all().delete()
        Statistic.objects.all().delete()
        AboutFact.objects.all().delete()
        TypedRole.objects.all().delete()
        SocialLink.objects.all().delete()
        PageIntro.objects.all().delete()
        SiteConfiguration.objects.all().delete()

        image_paths = self.build_site_image_assets(options.get("profile_source"))

        site = SiteConfiguration.objects.create(
            site_name="Rashid Zada",
            full_name="Rashid Zada",
            headline="Full Stack Developer | Computer Science Teacher | AI & Networking Specialist",
            hero_intro="I'm",
            about_heading="Full Stack Developer, Educator, and AI-Focused Problem Solver",
            professional_summary=(
                "Highly motivated Full Stack Developer and Computer Science Teacher with 5+ years of teaching "
                "experience and 3+ years of professional software development. Skilled in Python, Django, "
                "AI-integrated systems, Flutter, and CCNA-level networking concepts."
            ),
            about_intro=(
                "I teach Computer Science, IT, AI fundamentals, and practical programming with a strong focus on "
                "concept clarity, real-world projects, and future-ready skills."
            ),
            about_body=(
                "My work combines software engineering, AI integration, classroom delivery, and technical training. "
                "I am open to KSA and international opportunities where I can contribute to digital transformation, "
                "high-quality technical learning, and production-ready software systems."
            ),
            footer_summary=(
                "Full Stack Developer and Computer Science Teacher building practical Django systems, AI-ready "
                "solutions, and future-focused learning experiences."
            ),
            career_objective=(
                "To work as a Computer Science / IT Teacher or Full Stack Developer in Saudi Arabia or an "
                "international institution, contributing to AI education, digital transformation, and high-quality "
                "technical learning."
            ),
            location="Pakistan",
            availability="Open to KSA & International Opportunities",
            phone_display="0347 0983567",
            phone_link="+923470983567",
            whatsapp_number="923470983567",
            email="rashidzada6@gmail.com",
            portfolio_url="https://rashidzada.pythonanywhere.com",
            github_url="https://github.com/Rashidzada/Rashidzada",
            linkedin_url="https://www.linkedin.com/in/rashid-zada-14b309192/",
            typing_profile_url="https://keyhero.com/profile/user828295/",
            profile_image=image_paths["profile_image"],
            favicon_image=image_paths["favicon_image"],
            apple_touch_icon=image_paths["apple_touch_icon"],
            hero_background_image=image_paths["hero_background_image"],
        )

        page_intros = [
            (
                PageIntro.ABOUT,
                "About",
                "Professional profile, core capabilities, certifications, languages, strengths, and career focus.",
            ),
            (
                PageIntro.RESUME,
                "Resume",
                "A concise view of my professional summary, MSc Computer Science education, and hands-on experience.",
            ),
            (
                PageIntro.SERVICES,
                "Services",
                "Production Django development, AI integration, technical training, and practical systems support.",
            ),
            (
                PageIntro.PORTFOLIO,
                "Portfolio",
                "Selected projects spanning AI-enabled platforms, web systems, healthcare workflows, and education.",
            ),
            (
                PageIntro.CONTACT,
                "Contact",
                "Reach me directly through WhatsApp, phone, email, or my online professional profiles.",
            ),
            (
                PageIntro.STARTER,
                "Career Focus",
                "My objective, certifications, languages, and practical strengths for teaching and development roles.",
            ),
        ]
        for page_key, title, description in page_intros:
            PageIntro.objects.create(page_key=page_key, title=title, description=description)

        for order, role in enumerate(
            [
                "Full Stack Developer",
                "Computer Science Teacher",
                "AI & Networking Specialist",
            ],
            start=1,
        ):
            TypedRole.objects.create(name=role, order=order)

        social_links = [
            ("Portfolio", site.portfolio_url, "bi bi-globe2"),
            ("GitHub", site.github_url, "bi bi-github"),
            ("LinkedIn", site.linkedin_url, "bi bi-linkedin"),
            ("Typing Profile", site.typing_profile_url, "bi bi-keyboard"),
            ("WhatsApp", site.whatsapp_url, "bi bi-whatsapp"),
        ]
        for order, (label, url, icon_class) in enumerate(social_links, start=1):
            SocialLink.objects.create(
                label=label,
                url=url,
                icon_class=icon_class,
                order=order,
                show_in_hero=True,
                show_in_footer=True,
            )

        about_facts = [
            ("Location", site.location, "", 1),
            ("Availability", site.availability, "", 1),
            ("Portfolio", "rashidzada.pythonanywhere.com", site.portfolio_url, 1),
            ("GitHub", "Rashidzada/Rashidzada", site.github_url, 1),
            ("Phone", site.phone_display, "", 2),
            ("Email", site.email, "", 2),
            ("Degree", "MSc Computer Science", "", 2),
            ("Typing", "60+ WPM / 96% Accuracy", site.typing_profile_url, 2),
        ]
        for order, (label, value, link_url, column) in enumerate(about_facts, start=1):
            AboutFact.objects.create(
                label=label,
                value=value,
                link_url=link_url,
                column=column,
                order=order,
            )

        stats = [
            ("Development Years", 3, "+", "bi bi-code-slash"),
            ("Teaching Years", 5, "+", "bi bi-mortarboard"),
            ("Key Projects", 5, "", "bi bi-journal-richtext"),
            ("Technical Domains", 5, "", "bi bi-diagram-3"),
        ]
        for order, (label, value, suffix, icon_class) in enumerate(stats, start=1):
            Statistic.objects.create(
                label=label,
                value=value,
                suffix=suffix,
                icon_class=icon_class,
                order=order,
            )

        skills = [
            ("Python & Django", 95, 1),
            ("REST APIs", 90, 1),
            ("JavaScript", 82, 1),
            ("Flutter & Dart", 78, 2),
            ("AI Integration", 85, 2),
            ("Databases", 88, 2),
        ]
        for order, (name, proficiency, column) in enumerate(skills, start=1):
            Skill.objects.create(name=name, proficiency=proficiency, column=column, order=order)

        certifications = [
            ("Bachelor in Education (B.Ed.)", "bi bi-award", "#ffbb2c"),
            ("Diploma in Information Technology (DIT)", "bi bi-hdd-network", "#5578ff"),
            ("Flutter Training (Android & iOS)", "bi bi-phone", "#e80368"),
            ("Diploma in Teaching Education", "bi bi-book", "#e361ff"),
        ]
        for order, (title, icon_class, accent_color) in enumerate(certifications, start=1):
            Certification.objects.create(
                title=title,
                icon_class=icon_class,
                accent_color=accent_color,
                order=order,
            )

        languages = [
            ("English", "Conversational", "bi bi-translate", "#47aeff"),
            ("Urdu", "Fluent", "bi bi-chat-square-text", "#ffa76e"),
            ("Pashto", "Fluent", "bi bi-people", "#11dbcf"),
        ]
        for order, (name, proficiency, icon_class, accent_color) in enumerate(languages, start=1):
            Language.objects.create(
                name=name,
                proficiency=proficiency,
                icon_class=icon_class,
                accent_color=accent_color,
                order=order,
            )

        strengths = [
            ("Strong communication & analytical skills", "bi bi-lightbulb", "#4233ff"),
            ("Excellent classroom management", "bi bi-people-fill", "#b2904f"),
            ("Quick learner & problem solver", "bi bi-lightning-charge", "#b20969"),
            ("Disciplined, punctual, and goal-oriented", "bi bi-bullseye", "#ff5828"),
            ("Aligned with Saudi Vision 2030", "bi bi-globe-central-south-asia", "#29cc61"),
        ]
        for order, (title, icon_class, accent_color) in enumerate(strengths, start=1):
            Strength.objects.create(
                title=title,
                icon_class=icon_class,
                accent_color=accent_color,
                order=order,
            )

        highlights = [
            (
                "Production-Ready Web Systems",
                "Django Delivery",
                "Built full-stack Django applications, deployed production systems, and maintained real-world web platforms with practical business value.",
                "",
            ),
            (
                "Computer Science Education",
                "Grades 6 to Higher Education",
                "Delivered structured teaching in programming, databases, networking, and AI basics using concept-driven lessons, labs, and real-life examples.",
                "",
            ),
            (
                "AI & Technical Integration",
                "Modern Systems Thinking",
                "Worked with AI integration, machine learning fundamentals, automation, and network-aware system design to build future-ready technical solutions.",
                "",
            ),
            (
                "KSA & International Readiness",
                "Opportunity Focus",
                "Prepared for roles in Saudi Arabia and international environments with an emphasis on digital transformation, AI education, and standards-based delivery.",
                "",
            ),
            (
                "Career Objective",
                "Teaching or Development Role",
                site.career_objective,
                "",
            ),
        ]
        for order, (title, subtitle, description, image_path) in enumerate(highlights, start=1):
            ProfileHighlight.objects.create(
                title=title,
                subtitle=subtitle,
                description=description,
                image_path=image_path,
                order=order,
            )

        Education.objects.create(
            degree="MSc Computer Science",
            start_year=2016,
            end_year=2018,
            institution="University of Swat | Govt. P.G. Jahanzeb College, Saidu Sharif",
            description=(
                "Advanced study in Computer Science with a foundation that supports software development, teaching, "
                "practical programming, and modern technical problem solving."
            ),
            order=1,
        )

        experiences = [
            {
                "role_title": "Senior Full Stack Developer",
                "organization": "Remote",
                "location": "Production web systems",
                "start_label": "3+ Years",
                "end_label": "Present",
                "summary": "Designed, developed, deployed, and maintained Django-based production applications with AI-enabled workflows.",
                "bullets": [
                    "Designed and developed full-stack web applications using Django.",
                    "Integrated AI features into real-world systems.",
                    "Deployed and maintained production applications.",
                    "Delivered projects including qwo.pythonanywhere.com and hms.pythonanywhere.com.",
                ],
            },
            {
                "role_title": "Computer Instructor (DIT - Part Time)",
                "organization": "KTC Kabal",
                "location": "",
                "start_label": "Part Time",
                "end_label": "6 Months",
                "summary": "Delivered practical IT instruction for diploma-level learners.",
                "bullets": [
                    "Taught IT fundamentals, Office Automation, and basic programming.",
                    "Guided students in practical computer usage.",
                ],
            },
            {
                "role_title": "Computer Science Teacher",
                "organization": "Private & Government Institutions",
                "location": "",
                "start_label": "5+ Years",
                "end_label": "Present",
                "summary": "Taught Computer Science and IT with a focus on practical learning, labs, and future-ready technical concepts.",
                "bullets": [
                    "Taught Computer Science & IT for Grades 6-12.",
                    "Delivered lessons on programming, databases, networking, and AI basics.",
                    "Focused on hands-on labs and real-life examples.",
                    "Supported teacher and staff technical training where needed.",
                ],
            },
        ]
        for order, experience_data in enumerate(experiences, start=1):
            bullets = experience_data.pop("bullets")
            experience = Experience.objects.create(order=order, **experience_data)
            for bullet_order, bullet in enumerate(bullets, start=1):
                ExperienceBullet.objects.create(experience=experience, text=bullet, order=bullet_order)

        services = [
            {
                "title": "Django Web Application Development",
                "slug": "django-web-application-development",
                "icon_class": "bi bi-code-square",
                "short_description": "Design and build full-stack Django applications with clean architecture, admin workflows, and production deployment in mind.",
                "summary_heading": "Django systems built for real use",
                "summary_text": "I build structured Django applications for business workflows, dashboards, content systems, and scalable custom platforms.",
                "detail_heading": "Custom Django applications for production-ready delivery",
                "detail_intro": "From database design to templates, admin tools, and deployment, I create maintainable Django projects that solve real problems.",
                "detail_body": "This includes backend logic, data modeling, secure forms, static assets, content management, and practical hosting readiness for platforms such as PythonAnywhere.",
                "detail_footer": "The focus is always on code clarity, extensibility, and a product that can grow beyond a prototype.",
                "image_path": "assets/img/services/services-4.webp",
                "bullets": [
                    "Full-stack Django project architecture",
                    "Reusable apps, templates, and admin configuration",
                    "Production-oriented deployment structure",
                ],
            },
            {
                "title": "AI-Integrated Web Systems",
                "slug": "ai-integrated-web-systems",
                "icon_class": "bi bi-cpu",
                "short_description": "Integrate AI-assisted workflows into web platforms for smarter user experiences and business-focused automation.",
                "summary_heading": "AI where it adds practical value",
                "summary_text": "I work on systems where AI improves workflows, awareness platforms, and decision support without losing usability.",
                "detail_heading": "AI integration for real-world platforms",
                "detail_intro": "I combine Django backends with AI-aware features to support smarter transport, sustainability, and business workflows.",
                "detail_body": "The goal is not AI for show. It is AI that helps automate, guide, analyze, or improve the usefulness of a platform in practical scenarios.",
                "detail_footer": "This approach is reflected in projects such as RBT and Go Green Vision 2030.",
                "image_path": "assets/img/services/services-4.webp",
                "bullets": [
                    "AI-enabled workflow support",
                    "Machine learning fundamentals in product context",
                    "Business-focused system design",
                ],
            },
            {
                "title": "REST API & Database Development",
                "slug": "rest-api-and-database-development",
                "icon_class": "bi bi-database",
                "short_description": "Build structured APIs and reliable data layers using Django, SQLite, MySQL, PostgreSQL, and MongoDB concepts.",
                "summary_heading": "Reliable backend foundations",
                "summary_text": "Strong systems start with solid data design, maintainable models, and APIs that are easy to extend.",
                "detail_heading": "Backend logic, APIs, and data design",
                "detail_intro": "I design schemas and backend flows for secure, practical, and maintainable applications.",
                "detail_body": "This includes relational database work, role-aware data handling, API planning, and system structures that match the application's business logic.",
                "detail_footer": "The result is a backend that supports both rapid development and long-term maintainability.",
                "image_path": "assets/img/services/services-4.webp",
                "bullets": [
                    "Django models and relational data design",
                    "REST-style backend patterns",
                    "SQLite, MySQL, PostgreSQL, and MongoDB familiarity",
                ],
            },
            {
                "title": "Flutter Mobile Application Support",
                "slug": "flutter-mobile-application-support",
                "icon_class": "bi bi-phone",
                "short_description": "Support mobile solutions with Flutter and Dart for Android and iOS oriented application workflows.",
                "summary_heading": "Cross-platform mobile understanding",
                "summary_text": "I bring Flutter knowledge into projects where mobile support or app-oriented thinking is part of the solution.",
                "detail_heading": "Flutter and Dart capability for mobile experiences",
                "detail_intro": "My background includes formal Flutter training and practical understanding of Android and iOS app development workflows.",
                "detail_body": "This allows me to contribute to mobile-ready product thinking, app structures, and future expansion from web to mobile solutions.",
                "detail_footer": "It is especially useful when a system roadmap includes mobile users alongside a Django backend.",
                "image_path": "assets/img/services/services-4.webp",
                "bullets": [
                    "Flutter training for Android and iOS",
                    "Dart-based mobile app support",
                    "Web and mobile product alignment",
                ],
            },
            {
                "title": "Computer Science & IT Training",
                "slug": "computer-science-and-it-training",
                "icon_class": "bi bi-mortarboard",
                "short_description": "Teach Computer Science, IT, AI fundamentals, and practical programming through clear, project-based delivery.",
                "summary_heading": "Teaching with concept clarity",
                "summary_text": "I teach for understanding, not memorization, using practical examples, labs, and skill-building activities.",
                "detail_heading": "Technical teaching for students and staff",
                "detail_intro": "My teaching work covers Computer Science, IT, programming, databases, networking, AI basics, and practical digital skills.",
                "detail_body": "I have taught across private and government institutions, including Grades 6-12 and diploma-level learners, with an emphasis on hands-on understanding.",
                "detail_footer": "This work aligns strongly with future-ready education and Saudi Vision 2030 focused technical learning.",
                "image_path": "assets/img/services/services-4.webp",
                "bullets": [
                    "Computer Science and IT teaching",
                    "Project-based and concept-driven delivery",
                    "Teacher and staff technical training",
                ],
            },
            {
                "title": "Networking & Technical Systems Support",
                "slug": "networking-and-technical-systems-support",
                "icon_class": "bi bi-router",
                "short_description": "Support technical environments with networking fundamentals, system setup, troubleshooting, and classroom lab readiness.",
                "summary_heading": "Practical systems understanding",
                "summary_text": "Beyond software, I work with the system side of technical environments including networking concepts and troubleshooting.",
                "detail_heading": "Networking-aware technical support",
                "detail_intro": "My experience includes CCNA-level networking fundamentals, OS installation, system configuration, and practical issue resolution.",
                "detail_body": "This helps in classroom labs, training environments, and projects where stable technical infrastructure matters as much as application code.",
                "detail_footer": "It complements development work by keeping the broader technical environment reliable and usable.",
                "image_path": "assets/img/services/services-4.webp",
                "bullets": [
                    "CCNA-level networking fundamentals",
                    "OS installation and configuration",
                    "System troubleshooting and lab setup",
                ],
            },
        ]
        for order, service_data in enumerate(services, start=1):
            bullets = service_data.pop("bullets")
            service = Service.objects.create(order=order, **service_data)
            for bullet_order, bullet in enumerate(bullets, start=1):
                ServiceBullet.objects.create(service=service, text=bullet, order=bullet_order)

        categories = {}
        for order, (name, slug) in enumerate(
            [
                ("Web Apps", "web-apps"),
                ("AI Platforms", "ai-platforms"),
                ("Education & Training", "education-training"),
                ("Production Deployments", "production-deployments"),
            ],
            start=1,
        ):
            categories[slug] = ProjectCategory.objects.create(name=name, slug=slug, order=order)

        projects = [
            {
                "category": categories["ai-platforms"],
                "title": "RBT - AI Integrated Transportation Platform",
                "slug": "rbt-ai-integrated-transportation-platform",
                "summary": "AI-enabled transport management system with a scalable Django backend and business-oriented structure aligned with KSA transport needs.",
                "client": "Independent Product Concept",
                "project_date_label": "Production-ready case study",
                "project_url": "https://rbt.pythonanywhere.com/",
                "detail_heading": "AI-enabled transport management built with Django",
                "description": "RBT combines a scalable Django backend with AI-aware platform thinking for transportation workflows. The project is positioned around practical operations and KSA-aligned business needs.",
                "card_image": "assets/img/portfolio/portfolio-1.webp",
                "highlights": [
                    "AI-enabled transport management system",
                    "Django-based scalable backend",
                    "Business-focused design aligned with KSA transport needs",
                ],
                "images": [
                    "assets/img/portfolio/portfolio-1.webp",
                    "assets/img/portfolio/portfolio-10.webp",
                    "assets/img/portfolio/portfolio-7.webp",
                    "assets/img/portfolio/portfolio-4.webp",
                ],
            },
            {
                "category": categories["ai-platforms"],
                "title": "Go Green Vision 2030",
                "slug": "go-green-vision-2030",
                "summary": "Sustainability and AI awareness platform designed to communicate future-focused ideas through educational blogs and AI-driven sections.",
                "client": "Independent Initiative",
                "project_date_label": "Awareness platform",
                "project_url": "",
                "detail_heading": "Sustainability and AI awareness through digital content",
                "description": "Go Green Vision 2030 presents sustainability-focused messaging with AI-related content sections. It is designed as an educational and awareness-oriented platform with a future-ready theme.",
                "card_image": "assets/img/portfolio/portfolio-10.webp",
                "highlights": [
                    "Sustainability and AI awareness platform",
                    "Educational blog-driven structure",
                    "Future-focused messaging aligned with Vision 2030 themes",
                ],
                "images": [
                    "assets/img/portfolio/portfolio-10.webp",
                    "assets/img/portfolio/portfolio-11.webp",
                    "assets/img/portfolio/portfolio-12.webp",
                    "assets/img/portfolio/portfolio-9.webp",
                ],
            },
            {
                "category": categories["production-deployments"],
                "title": "Health Management System (HMS)",
                "slug": "health-management-system",
                "summary": "Full-stack healthcare workflow automation platform with secure data handling and role-based access patterns.",
                "client": "Production Deployment",
                "project_date_label": "Live deployment",
                "project_url": "https://hms.pythonanywhere.com",
                "detail_heading": "Healthcare workflow automation with secure access control",
                "description": "The Health Management System focuses on operational workflow automation in a healthcare setting. It emphasizes secure handling of data, structured access, and backend reliability.",
                "card_image": "assets/img/portfolio/portfolio-7.webp",
                "highlights": [
                    "Full-stack healthcare workflow automation",
                    "Secure data handling",
                    "Role-based access support",
                ],
                "images": [
                    "assets/img/portfolio/portfolio-7.webp",
                    "assets/img/portfolio/portfolio-8.webp",
                    "assets/img/portfolio/portfolio-9.webp",
                    "assets/img/portfolio/portfolio-6.webp",
                ],
            },
            {
                "category": categories["production-deployments"],
                "title": "QWO Django Platform",
                "slug": "qwo-django-platform",
                "summary": "A deployed Django-based web platform representing hands-on production work and maintenance capability.",
                "client": "Production Deployment",
                "project_date_label": "Live deployment",
                "project_url": "https://qwo.pythonanywhere.com",
                "detail_heading": "Production Django deployment with maintainable backend structure",
                "description": "QWO reflects practical work in building, deploying, and maintaining Django applications in a live environment. It demonstrates operational readiness and backend ownership.",
                "card_image": "assets/img/portfolio/portfolio-4.webp",
                "highlights": [
                    "Live Django application deployment",
                    "Production maintenance capability",
                    "Backend structure built for practical use",
                ],
                "images": [
                    "assets/img/portfolio/portfolio-4.webp",
                    "assets/img/portfolio/portfolio-5.webp",
                    "assets/img/portfolio/portfolio-6.webp",
                    "assets/img/portfolio/portfolio-3.webp",
                ],
            },
            {
                "category": categories["education-training"],
                "title": "Computer Science Training Programs",
                "slug": "computer-science-training-programs",
                "summary": "Teaching-focused delivery covering Computer Science, IT, AI basics, databases, networking, and project-based learning.",
                "client": "Private & Government Institutions",
                "project_date_label": "5+ years of delivery",
                "project_url": "",
                "detail_heading": "Practical training for Computer Science and IT learners",
                "description": "This body of work represents long-term instructional delivery across private and government institutions, combining classroom teaching with practical labs, technical mentoring, and staff support.",
                "card_image": "assets/img/portfolio/portfolio-2.webp",
                "highlights": [
                    "Computer Science and IT instruction for Grades 6-12",
                    "Programming, databases, networking, and AI basics",
                    "Project-based teaching with practical lab support",
                ],
                "images": [
                    "assets/img/portfolio/portfolio-2.webp",
                    "assets/img/portfolio/portfolio-3.webp",
                    "assets/img/portfolio/portfolio-11.webp",
                    "assets/img/portfolio/portfolio-12.webp",
                ],
            },
        ]
        for order, project_data in enumerate(projects, start=1):
            highlights = project_data.pop("highlights")
            images = project_data.pop("images")
            project = Project.objects.create(order=order, **project_data)
            for highlight_order, highlight in enumerate(highlights, start=1):
                ProjectHighlight.objects.create(project=project, text=highlight, order=highlight_order)
            for image_order, image_path in enumerate(images, start=1):
                ProjectImage.objects.create(project=project, image_path=image_path, order=image_order)

        self.stdout.write(self.style.SUCCESS("Portfolio content seeded successfully."))
