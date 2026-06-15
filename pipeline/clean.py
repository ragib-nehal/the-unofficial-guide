from __future__ import annotations

import html
import re
from dataclasses import dataclass
from pathlib import Path

from .config import PipelinePaths
from .load import Document


@dataclass(frozen=True)
class CleanedDocument:
    source_id: int
    source_type: str
    source_file: str
    url: str
    text: str
    metadata: dict[str, str | int]


TAGS = {
    "Accessible outside class",
    "Amazing lectures",
    "Beware of pop quizzes",
    "Caring",
    "Clear grading criteria",
    "Extra credit",
    "Get ready to read",
    "Gives good feedback",
    "Graded by few things",
    "Group projects",
    "Helpful",
    "Hilarious",
    "Inspirational",
    "Lecture heavy",
    "Lots of homework",
    "Online Savvy",
    "Participation matters",
    "Respected",
    "Skip class? You won't pass.",
    "So many papers",
    "Test heavy",
    "Tough grader",
}

BOILERPLATE_PREFIXES = (
    "Logo",
    "Professors",
    "Caret Down",
    "Professor name",
    "Your school",
    "Log In",
    "Sign Up",
    "Help",
    "Rate",
    "Compare",
    "I'm Professor",
    "Rating Distribution",
    "Similar Professors",
    "Load More Ratings",
    "Tech News",
    "Rate My Professors",
    "Copyright",
    "Privacy Policy",
    "Terms & Conditions",
    "Do Not Sell",
    "CA Notice",
    "Site Guidelines",
    "The video player",
    "Sam Bankman",
)


def clean_documents(documents: list[Document]) -> list[CleanedDocument]:
    return [clean_document(document) for document in documents]


def clean_document(document: Document) -> CleanedDocument:
    if document.source_type == "rmp":
        text = clean_rmp(document)
    elif document.source_type == "coursicle":
        text = clean_coursicle(document)
    elif document.source_type == "bc_cis":
        text = clean_bc(document)
    elif document.source_type == "pdf":
        text = clean_pdf(document.raw_text)
    else:
        text = normalize_text(document.raw_text)

    return CleanedDocument(
        source_id=document.source_id,
        source_type=document.source_type,
        source_file=document.source_file,
        url=document.url,
        text=text,
        metadata=dict(document.metadata),
    )


def write_cleaned_documents(
    cleaned_documents: list[CleanedDocument], paths: PipelinePaths | None = None
) -> None:
    paths = paths or PipelinePaths()
    paths.cleaned_dir.mkdir(parents=True, exist_ok=True)
    for document in cleaned_documents:
        output_name = Path(document.source_file).with_suffix(".txt").name
        (paths.cleaned_dir / output_name).write_text(document.text + "\n", encoding="utf-8")


def clean_rmp(document: Document) -> str:
    lines = normalized_lines(document.raw_text)
    lines = _trim_after_prefix(lines, ("Load More Ratings", "Tech News"))
    professor = str(document.metadata.get("professor_name", "Unknown Professor"))
    header = f"PROFESSOR: {professor} | Computer Science | Brooklyn College"
    reviews = _parse_rmp_reviews(lines)
    if not reviews:
        body = normalize_text("\n".join(_remove_boilerplate(lines)))
        return f"{header}\n---\nREVIEW: {body}".strip()
    return f"{header}\n---\n" + "\n---\n".join(reviews)


def clean_coursicle(document: Document) -> str:
    lines = normalized_lines(document.raw_text)
    filtered = []
    skip_next = False
    for line in lines:
        if skip_next:
            skip_next = False
            continue
        if line in {"CISC at BC", "Professor Reviews"}:
            continue
        if line.startswith(("Read all ", "View Fall ", "👟 Track")):
            continue
        if line.startswith(("We made WalkNYC", "Fall 2026 Sections")):
            continue
        if line in {"Recent Professors", "Recent Semesters"}:
            skip_next = True
            continue
        filtered.append(line)

    title = next((line for line in filtered if re.match(r"^CISC \w+ - ", line)), "")
    course_number = str(document.metadata.get("course_number", _course_number_from_text(title)))
    sections = [f"COURSE: {course_number}", f"TITLE: {title}"] if title else [f"COURSE: {course_number}"]

    description_index = _index_of(filtered, "Description")
    if description_index != -1:
        review_lines = filtered[filtered.index(title) + 1 : description_index] if title in filtered else filtered[:description_index]
        description_lines = filtered[description_index + 1 :]
    else:
        review_lines = filtered[filtered.index(title) + 1 :] if title in filtered else filtered
        description_lines = []

    if review_lines:
        sections.append("REVIEWS:\n" + _format_coursicle_reviews(review_lines))
    if description_lines:
        sections.append("DESCRIPTION:\n" + normalize_text("\n".join(description_lines)))
    return "\n\n".join(section for section in sections if section.strip()).strip()


def clean_bc(document: Document) -> str:
    lines = normalized_lines(document.raw_text)
    filtered: list[str] = []
    footer_markers = (
        "Advice for students considering",
        "This website powered by",
        "Questions? Consult",
    )
    for line in lines:
        if line in {"PREVIOUS", "NEXT"}:
            continue
        if line.startswith(footer_markers):
            break
        filtered.append(line)
    return normalize_text("\n".join(filtered))


def clean_pdf(text: str) -> str:
    text = html.unescape(text)
    replacements = {
        "ww w": "www",
        "departm ents": "departments",
        "inform ation": "information",
        "prereq uisite": "prerequisite",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    pages = [page.strip() for page in re.split(r"(?=PAGE \d+\n)", text) if page.strip()]
    substantive_pages = [
        page
        for page in pages
        if "TABLE OF CONTENTS" not in page
        and not re.match(r"PAGE 1\nADVICE\nto\nUNDERGRADUATES", page)
    ]
    return normalize_text("\n\n".join(substantive_pages))


def normalize_text(text: str) -> str:
    text = html.unescape(text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return "\n".join(line.strip() for line in text.splitlines()).strip()


def normalized_lines(text: str) -> list[str]:
    return [line for line in (normalize_text(text).splitlines()) if line]


def _remove_boilerplate(lines: list[str]) -> list[str]:
    cleaned: list[str] = []
    for line in lines:
        if line.startswith(BOILERPLATE_PREFIXES):
            continue
        if line in {"Thumbs up", "Thumbs down"}:
            continue
        cleaned.append(line)
    return cleaned


def _trim_after_prefix(lines: list[str], prefixes: tuple[str, ...]) -> list[str]:
    trimmed: list[str] = []
    for line in lines:
        if line.startswith(prefixes):
            break
        trimmed.append(line)
    return trimmed


def _parse_rmp_reviews(lines: list[str]) -> list[str]:
    reviews: list[str] = []
    index = 0
    while index < len(lines):
        if lines[index] != "Quality" or index + 5 >= len(lines):
            index += 1
            continue
        quality = lines[index + 1]
        if lines[index + 2] != "Difficulty":
            index += 1
            continue
        difficulty = lines[index + 3]
        course = lines[index + 4]
        date = lines[index + 5]
        index += 6

        fields: list[str] = []
        payload: list[str] = []
        while index < len(lines) and lines[index] != "Quality":
            line = lines[index]
            if _is_trailing_next_review_hint(lines, index):
                index += 1
                continue
            if line in {"Thumbs up", "Thumbs down"}:
                index += 2
                continue
            if line.startswith("Reviewed:"):
                index += 1
                while index < len(lines) and lines[index] != "Quality":
                    index += 1
                continue
            if line.startswith(BOILERPLATE_PREFIXES):
                index += 1
                continue
            if ":" in line and not payload:
                fields.append(line)
            else:
                payload.append(line)
            index += 1

        review_lines: list[str] = []
        tag_lines: list[str] = []
        for line in payload:
            if line.isdigit():
                continue
            review_fragment, tags = _extract_rmp_tags(line)
            if review_fragment:
                review_lines.append(review_fragment)
            tag_lines.extend(tags)
        review_text = " ".join(review_lines).strip()
        if not review_text:
            continue
        field_text = " | ".join(fields)
        parts = [f"QUALITY: {quality} | DIFFICULTY: {difficulty} | COURSE: {course} | DATE: {date}"]
        if field_text:
            parts.append(f"DETAILS: {field_text}")
        parts.append(f"REVIEW: {review_text}")
        if tag_lines:
            parts.append("TAGS: " + ", ".join(dict.fromkeys(tag_lines)))
        reviews.append("\n".join(parts))
    return reviews


def _extract_rmp_tags(line: str) -> tuple[str, list[str]]:
    tags = [tag for tag in TAGS if tag in line]
    fragment = line
    for tag in tags:
        fragment = fragment.replace(tag, " ")
    return " ".join(fragment.split()), sorted(tags, key=line.find)


def _is_trailing_next_review_hint(lines: list[str], index: int) -> bool:
    line = lines[index]
    next_line = lines[index + 1] if index + 1 < len(lines) else ""
    following_line = lines[index + 2] if index + 2 < len(lines) else ""
    if _is_course_code(line) and _is_review_date(next_line) and following_line == "Quality":
        return True
    if _is_review_date(line) and next_line == "Quality":
        return True
    return False


def _is_course_code(line: str) -> bool:
    return bool(re.fullmatch(r"[A-Z]{2,5}\d{4}[A-Z]?", line))


def _is_review_date(line: str) -> bool:
    return bool(re.fullmatch(r"[A-Z][a-z]{2} \d{1,2}(st|nd|rd|th), \d{4}", line))


def _format_coursicle_reviews(lines: list[str]) -> str:
    return normalize_text("\n".join(lines))


def _course_number_from_text(text: str) -> str:
    match = re.search(r"\bCISC\s+\w+", text)
    return match.group(0) if match else ""


def _index_of(lines: list[str], value: str) -> int:
    try:
        return lines.index(value)
    except ValueError:
        return -1
