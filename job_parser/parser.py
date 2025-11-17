"""Job posting parser that converts raw text into structured JSON."""

from typing import Dict, List, Tuple

from job_parser.utils.cleaning import clean_text
from job_parser.utils.header_detection import find_best_field_match, group_sections


DEFAULT_SECTION_TEMPLATE = {
    "キャッチコピー": "",
    "勤務地": "",
    "仕事内容": "",
    "求めている人材": "",
    "勤務時間": "",
    "勤務時間詳細": "",
    "勤務地所在地": "",
    "交通アクセス": "",
    "給与詳細": "",
    "試用期間": "",
    "待遇・福利厚生": "",
    "社会保険": "",
    "選考プロセス": "",
}


def _guess_primary_fields(lines: List[str], sections: Dict[str, str]) -> Tuple[str, str, str]:
    """Infer job_title, company, and salary from both free-form lines and sections."""
    job_title = ""
    company = ""
    salary = ""

    # Use first non-empty lines as potential title/company fallback
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    if non_empty_lines:
        job_title = non_empty_lines[0]
        if len(non_empty_lines) > 1:
            company = non_empty_lines[1]

    # Improve guesses from section headers
    for header, body in sections.items():
        field = find_best_field_match(header)
        if field == "job_title" and body:
            job_title = body.split("\n")[0]
        elif field == "company" and body:
            company = body.split("\n")[0]
        elif field == "salary" and body:
            salary = body

    # Try inline salary capture from any line
    if not salary:
        for line in non_empty_lines:
            if any(key in line for key in ["給与", "年収", "月給", "時給", "日給", "賞与"]):
                salary = line
                break

    # Company detection via common suffixes
    if not company:
        for line in non_empty_lines:
            if any(keyword in line for keyword in ["株式会社", "有限会社", "合同会社", "Inc", "LLC", "Co."]):
                company = line
                break

    # Replace header-looking titles with meaningful section content
    if not job_title or job_title.startswith(("【", "[")):
        for body in sections.values():
            if body.strip():
                job_title = body.split("\n")[0]
                break

    return job_title, company, salary


def _merge_sections(detected_sections: Dict[str, str]) -> Dict[str, str]:
    merged = {**DEFAULT_SECTION_TEMPLATE}
    for header, body in detected_sections.items():
        # Preserve original header wording; if it matches a default key, override
        merged[header] = body
    return merged


def parse_job(raw_text: str) -> Dict[str, object]:
    """Parse raw job posting text into structured JSON-like dictionary."""
    cleaned = clean_text(raw_text)
    lines = cleaned.split("\n")

    detected_sections = group_sections(lines)
    job_title, company, salary = _guess_primary_fields(lines, detected_sections)
    sections = _merge_sections(detected_sections)

    return {
        "job_title": job_title,
        "company": company,
        "salary": salary,
        "sections": sections,
    }
