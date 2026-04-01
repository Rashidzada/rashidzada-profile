import os
import re

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - exercised only when dependency is missing
    OpenAI = None

from .profile_api import build_profile_payload


PROFILE_ONLY_REPLY = (
    "I only answer questions about Rashid Zada's profile, services, projects, "
    "skills, experience, education, and contact details."
)
GENERIC_PROFILE_HINTS = {
    "rashid",
    "zada",
    "profile",
    "portfolio",
    "resume",
    "cv",
    "about",
    "contact",
    "email",
    "phone",
    "whatsapp",
    "hire",
    "developer",
    "teacher",
    "educator",
    "experience",
    "education",
    "degree",
    "msc",
    "skills",
    "services",
    "projects",
    "github",
    "linkedin",
    "availability",
    "location",
    "technology",
    "django",
    "python",
    "flutter",
    "ai",
    "networking",
}
STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "at",
    "be",
    "can",
    "do",
    "for",
    "from",
    "get",
    "how",
    "i",
    "in",
    "is",
    "it",
    "me",
    "of",
    "on",
    "or",
    "please",
    "tell",
    "the",
    "to",
    "what",
    "who",
    "with",
    "you",
    "your",
}


def tokenize(text):
    return {
        token
        for token in re.findall(r"[a-z0-9]+", (text or "").lower())
        if len(token) > 2 and token not in STOP_WORDS
    }


def build_profile_context(payload):
    site = payload.get("site", {})
    sections = []

    if site:
        sections.append(
            "\n".join(
                [
                    f"Name: {site.get('full_name', '')}",
                    f"Headline: {site.get('headline', '')}",
                    f"Summary: {site.get('professional_summary', '')}",
                    f"About: {site.get('about_intro', '')} {site.get('about_body', '')}".strip(),
                    (
                        "Contact: "
                        f"phone {site.get('phone_display', '')}, "
                        f"email {site.get('email', '')}, "
                        f"WhatsApp {site.get('whatsapp_number', '')}, "
                        f"portfolio {site.get('portfolio_url', '')}, "
                        f"GitHub {site.get('github_url', '')}, "
                        f"LinkedIn {site.get('linkedin_url', '')}"
                    ),
                    f"Location: {site.get('location', '')}",
                    f"Availability: {site.get('availability', '')}",
                    f"Career objective: {site.get('career_objective', '')}",
                ]
            )
        )

    roles = ", ".join(role["name"] for role in payload.get("typed_roles", []))
    if roles:
        sections.append(f"Roles: {roles}")

    skills = ", ".join(skill["name"] for skill in payload.get("skills", []))
    if skills:
        sections.append(f"Skills: {skills}")

    services = []
    for service in payload.get("services", []):
        services.append(
            f"{service['title']}: {service['short_description']} "
            f"Summary: {service['summary_text']}"
        )
    if services:
        sections.append("Services:\n" + "\n".join(services))

    projects = []
    for project in payload.get("projects", []):
        projects.append(
            f"{project['title']} ({project['category']['name']}): {project['summary']} "
            f"URL: {project['project_url'] or 'Not listed'}"
        )
    if projects:
        sections.append("Projects:\n" + "\n".join(projects))

    experience_lines = []
    for experience in payload.get("experiences", []):
        bullets = "; ".join(item["text"] for item in experience.get("bullets", []))
        experience_lines.append(
            f"{experience['role_title']} at {experience['organization']} "
            f"({experience['period_label']}): {experience['summary']} {bullets}".strip()
        )
    if experience_lines:
        sections.append("Experience:\n" + "\n".join(experience_lines))

    education_lines = []
    for education in payload.get("education", []):
        education_lines.append(
            f"{education['degree']} at {education['institution']} "
            f"({education['start_year']}-{education['end_year']}): {education['description']}"
        )
    if education_lines:
        sections.append("Education:\n" + "\n".join(education_lines))

    return "\n\n".join(section for section in sections if section).strip()


def build_search_chunks(payload):
    site = payload.get("site", {})
    chunks = []

    if site:
        chunks.extend(
            [
                {
                    "title": "Profile Summary",
                    "text": f"{site.get('headline', '')}. {site.get('professional_summary', '')}",
                },
                {
                    "title": "Contact",
                    "text": (
                        f"Phone {site.get('phone_display', '')}. "
                        f"Email {site.get('email', '')}. "
                        f"WhatsApp {site.get('whatsapp_number', '')}. "
                        f"Portfolio {site.get('portfolio_url', '')}. "
                        f"GitHub {site.get('github_url', '')}. "
                        f"LinkedIn {site.get('linkedin_url', '')}."
                    ),
                },
                {
                    "title": "Availability",
                    "text": (
                        f"Location {site.get('location', '')}. "
                        f"Availability {site.get('availability', '')}. "
                        f"Career objective: {site.get('career_objective', '')}"
                    ),
                },
            ]
        )

    if payload.get("typed_roles"):
        chunks.append(
            {
                "title": "Roles",
                "text": ", ".join(item["name"] for item in payload["typed_roles"]),
            }
        )

    if payload.get("skills"):
        chunks.append(
            {
                "title": "Skills",
                "text": ", ".join(
                    f"{item['name']} ({item['proficiency']}%)" for item in payload["skills"]
                ),
            }
        )

    for experience in payload.get("experiences", []):
        chunks.append(
            {
                "title": experience["role_title"],
                "text": " ".join(
                    [
                        f"{experience['role_title']} at {experience['organization']}.",
                        experience["summary"],
                        " ".join(item["text"] for item in experience.get("bullets", [])),
                    ]
                ).strip(),
            }
        )

    for education in payload.get("education", []):
        chunks.append(
            {
                "title": education["degree"],
                "text": (
                    f"{education['degree']} at {education['institution']} from "
                    f"{education['start_year']} to {education['end_year']}. "
                    f"{education['description']}"
                ),
            }
        )

    for service in payload.get("services", []):
        chunks.append(
            {
                "title": service["title"],
                "text": " ".join(
                    [
                        service["short_description"],
                        service["summary_text"],
                        service["detail_intro"],
                        service["detail_body"],
                    ]
                ).strip(),
            }
        )

    for project in payload.get("projects", []):
        chunks.append(
            {
                "title": project["title"],
                "text": " ".join(
                    [
                        project["summary"],
                        project["description"],
                        project["category"]["name"],
                        " ".join(item["text"] for item in project.get("highlights", [])),
                        project["project_url"] or "",
                    ]
                ).strip(),
            }
        )

    return chunks


def build_profile_keywords(payload):
    keywords = set(GENERIC_PROFILE_HINTS)
    site = payload.get("site", {})
    text_values = [
        site.get("full_name", ""),
        site.get("headline", ""),
        site.get("site_name", ""),
        site.get("about_heading", ""),
        site.get("location", ""),
        site.get("availability", ""),
    ]
    for collection_key in (
        "typed_roles",
        "skills",
        "services",
        "projects",
        "project_categories",
        "education",
        "experiences",
        "languages",
        "strengths",
        "certifications",
    ):
        for item in payload.get(collection_key, []):
            for value in item.values():
                if isinstance(value, str):
                    text_values.append(value)

    for value in text_values:
        keywords.update(tokenize(value))
    return keywords


def is_profile_question(question, payload):
    normalized_question = (question or "").strip().lower()
    if not normalized_question:
        return False

    if any(
        phrase in normalized_question
        for phrase in (
            "who are you",
            "tell me about rashid",
            "tell me about you",
            "what do you do",
            "how can i contact",
            "how to contact",
            "what services",
            "which projects",
        )
    ):
        return True

    question_tokens = tokenize(normalized_question)
    if not question_tokens:
        return False
    return bool(question_tokens.intersection(build_profile_keywords(payload)))


def answer_common_intent(question, payload):
    normalized_question = (question or "").lower()
    site = payload.get("site", {})

    if any(keyword in normalized_question for keyword in ("contact", "phone", "email", "whatsapp", "call")):
        return (
            f"You can contact Rashid Zada by phone at {site.get('phone_display', 'not listed')}, "
            f"email at {site.get('email', 'not listed')}, or WhatsApp at {site.get('whatsapp_number', 'not listed')}. "
            f"Portfolio: {site.get('portfolio_url', 'not listed')}."
        )

    if any(keyword in normalized_question for keyword in ("skill", "technology", "stack", "tools")):
        skill_text = ", ".join(item["name"] for item in payload.get("skills", []))
        return f"Rashid Zada's main skills include {skill_text}."

    if any(keyword in normalized_question for keyword in ("service", "offer", "help", "provide")):
        service_text = "; ".join(item["title"] for item in payload.get("services", []))
        return f"Rashid Zada offers these services: {service_text}."

    if any(keyword in normalized_question for keyword in ("project", "portfolio", "work", "built")):
        project_text = "; ".join(item["title"] for item in payload.get("projects", []))
        return f"Featured projects include {project_text}."

    if any(keyword in normalized_question for keyword in ("education", "degree", "study", "msc")):
        education_items = payload.get("education", [])
        if not education_items:
            return "The site currently lists MSc Computer Science as Rashid Zada's education."
        education = education_items[0]
        return (
            f"Rashid Zada's listed education is {education['degree']} from "
            f"{education['institution']} ({education['start_year']}-{education['end_year']})."
        )

    if any(keyword in normalized_question for keyword in ("experience", "teaching", "developer", "teacher")):
        experiences = payload.get("experiences", [])
        experience_lines = [
            f"{item['role_title']} at {item['organization']} ({item['period_label']})"
            for item in experiences[:3]
        ]
        return "Rashid Zada's experience includes " + "; ".join(experience_lines) + "."

    if any(keyword in normalized_question for keyword in ("availability", "location", "relocate", "country")):
        return (
            f"Rashid Zada is based in {site.get('location', 'Pakistan')} and is "
            f"{site.get('availability', 'available for opportunities')}."
        )

    return ""


def fallback_answer(question, payload):
    common_intent_reply = answer_common_intent(question, payload)
    if common_intent_reply:
        return common_intent_reply

    question_tokens = tokenize(question)
    scored_chunks = []
    for chunk in build_search_chunks(payload):
        chunk_tokens = tokenize(f"{chunk['title']} {chunk['text']}")
        score = len(question_tokens.intersection(chunk_tokens))
        if score:
            scored_chunks.append((score, chunk))

    scored_chunks.sort(key=lambda item: item[0], reverse=True)
    if not scored_chunks:
        site = payload.get("site", {})
        return (
            f"{site.get('full_name', 'Rashid Zada')} is a "
            f"{site.get('headline', 'Full Stack Developer')}. "
            f"{site.get('professional_summary', '')}".strip()
        )

    top_chunks = [chunk for _, chunk in scored_chunks[:2]]
    parts = [f"{chunk['title']}: {chunk['text']}" for chunk in top_chunks]
    return " ".join(parts)


def get_remote_answer(question, payload):
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key or OpenAI is None:
        return ""

    client = OpenAI(
        api_key=api_key,
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").strip(),
    )
    response = client.chat.completions.create(
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip(),
        temperature=0.2,
        max_tokens=400,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are Snail Bot, the profile assistant for Rashid Zada. "
                    "Answer only questions about Rashid Zada's profile, projects, services, "
                    "skills, experience, education, availability, and contact details. "
                    "Use only the supplied profile context. If the answer is not in the context, "
                    "say it is not listed. If the question is unrelated, refuse briefly."
                ),
            },
            {
                "role": "system",
                "content": f"Profile context:\n{build_profile_context(payload)}",
            },
            {
                "role": "user",
                "content": question.strip(),
            },
        ],
    )
    return (response.choices[0].message.content or "").strip()


def get_snail_bot_reply(question):
    payload = build_profile_payload()
    site = payload.get("site", {})
    assistant_name = site.get("assistant_name", "Snail Bot")
    question_text = (question or "").strip()

    if not question_text:
        return {
            "assistant": assistant_name,
            "related": True,
            "mode": "local",
            "message": site.get("assistant_greeting") or PROFILE_ONLY_REPLY,
        }

    if not is_profile_question(question_text, payload):
        return {
            "assistant": assistant_name,
            "related": False,
            "mode": "guard",
            "message": PROFILE_ONLY_REPLY,
        }

    remote_error = ""
    remote_message = ""
    try:
        remote_message = get_remote_answer(question_text, payload)
    except Exception as exc:  # pragma: no cover - network/provider failures are environment-specific
        remote_error = str(exc)

    if remote_message:
        return {
            "assistant": assistant_name,
            "related": True,
            "mode": "deepseek",
            "message": remote_message,
        }

    fallback_message = fallback_answer(question_text, payload)
    response = {
        "assistant": assistant_name,
        "related": True,
        "mode": "local",
        "message": fallback_message,
    }
    if remote_error:
        response["provider_error"] = remote_error
    return response
