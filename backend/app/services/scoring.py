from __future__ import annotations

import re
from collections import Counter
from typing import Any


# ============================================================
# HIREX GENERIC ATS ENGINE
# ============================================================
#
# Design principles:
#
# 1. Job-role independent
# 2. Recruiter-defined required/optional skills drive matching
# 3. Explicit technology evidence is strongest
# 4. Project/experience evidence can demonstrate capabilities
# 5. Technical models/methods can provide RELATED evidence
# 6. Related evidence must NOT be presented as explicit usage
# 7. Sentence quality and technical expression matter
# 8. Education contributes ZERO to ATS score
# 9. Education is evaluated separately as an eligibility filter
# 10. Avoid keyword stuffing
#
# ============================================================


# ============================================================
# SCORE WEIGHTS
# ============================================================
#
# Education is intentionally NOT included.
#
# Total = 100
# ============================================================

WEIGHTS = {
    "required": 40,
    "optional": 10,
    "semantic_relevance": 10,
    "experience": 10,
    "projects": 15,
    "certifications": 5,
    "resume_quality": 5,
    "technical_expression": 5,
}


EDUCATION_THRESHOLD = 60


# ============================================================
# NORMALIZATION
# ============================================================

def normalize(text: str) -> str:
    """
    Normalize text for comparison while preserving useful
    technical terms such as C++, C#, .NET, Node.js, etc.
    """
    if not text:
        return ""

    text = str(text).lower()

    replacements = {
        "node js": "node.js",
        "nodejs": "node.js",
        "next js": "next.js",
        "nextjs": "next.js",
        "react js": "react",
        "reactjs": "react",
        "vue js": "vue",
        "vuejs": "vue",
        "angular js": "angular",
        "scikit learn": "scikit-learn",
        "sklearn": "scikit-learn",
        "power bi": "powerbi",
        "machine-learning": "machine learning",
        "deep-learning": "deep learning",
        "natural-language-processing": "natural language processing",
        "computer-vision": "computer vision",
        "restful api": "rest api",
        "restful apis": "rest api",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"[\u2013\u2014]", "-", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def clean_skill(skill: str) -> str:
    return normalize(skill).strip(" ,;|:-")


def unique(items: list[str]) -> list[str]:
    seen = set()
    result = []

    for item in items:
        key = clean_skill(item)
        if key and key not in seen:
            seen.add(key)
            result.append(item.strip())

    return result


# ============================================================
# GENERIC SKILL ALIASES
# ============================================================
#
# These are NOT used to decide what job the candidate is applying
# for. They only help recognize common ways a skill can appear.
#
# The recruiter can still provide completely new skills.
# ============================================================

ALIASES = {
    "python": [
        "python",
        "python programming",
        "python language",
    ],
    "java": [
        "java",
        "java programming",
        "core java",
    ],
    "javascript": [
        "javascript",
        "js",
        "ecmascript",
    ],
    "typescript": [
        "typescript",
        "ts",
    ],
    "c": [
        "c programming",
        "c language",
    ],
    "c++": [
        "c++",
        "cpp",
    ],
    "c#": [
        "c#",
        "c sharp",
    ],
    "sql": [
        "sql",
        "structured query language",
    ],
    "html": [
        "html",
        "html5",
    ],
    "css": [
        "css",
        "css3",
    ],
    "react": [
        "react",
        "react.js",
        "reactjs",
    ],
    "angular": [
        "angular",
        "angular.js",
        "angularjs",
    ],
    "vue": [
        "vue",
        "vue.js",
        "vuejs",
    ],
    "node.js": [
        "node.js",
        "nodejs",
        "node js",
    ],
    "express.js": [
        "express",
        "express.js",
        "expressjs",
    ],
    "django": [
        "django",
    ],
    "flask": [
        "flask",
    ],
    "spring": [
        "spring",
        "spring framework",
        "spring boot",
    ],
    "spring boot": [
        "spring boot",
    ],
    "php": [
        "php",
    ],
    "mysql": [
        "mysql",
    ],
    "postgresql": [
        "postgresql",
        "postgres",
    ],
    "mongodb": [
        "mongodb",
        "mongo db",
    ],
    "sqlite": [
        "sqlite",
    ],
    "oracle": [
        "oracle database",
        "oracle db",
    ],
    "git": [
        "git",
    ],
    "github": [
        "github",
    ],
    "docker": [
        "docker",
        "containerization",
        "containers",
    ],
    "kubernetes": [
        "kubernetes",
        "k8s",
    ],
    "aws": [
        "aws",
        "amazon web services",
    ],
    "azure": [
        "azure",
        "microsoft azure",
    ],
    "gcp": [
        "gcp",
        "google cloud",
        "google cloud platform",
    ],
    "linux": [
        "linux",
    ],
    "ci/cd": [
        "ci/cd",
        "continuous integration",
        "continuous deployment",
        "continuous delivery",
    ],
    "jenkins": [
        "jenkins",
    ],
    "machine learning": [
        "machine learning",
        "machine-learning",
        "ml",
    ],
    "deep learning": [
        "deep learning",
        "deep-learning",
        "dl",
    ],
    "artificial intelligence": [
        "artificial intelligence",
        "ai",
    ],
    "natural language processing": [
        "natural language processing",
        "nlp",
    ],
    "computer vision": [
        "computer vision",
        "computer-vision",
    ],
    "scikit-learn": [
        "scikit-learn",
        "scikit learn",
        "sklearn",
    ],
    "tensorflow": [
        "tensorflow",
    ],
    "keras": [
        "keras",
    ],
    "pytorch": [
        "pytorch",
        "torch",
    ],
    "numpy": [
        "numpy",
    ],
    "pandas": [
        "pandas",
    ],
    "matplotlib": [
        "matplotlib",
    ],
    "seaborn": [
        "seaborn",
    ],
    "opencv": [
        "opencv",
        "cv2",
    ],
    "spark": [
        "apache spark",
        "spark",
        "pyspark",
    ],
    "tableau": [
        "tableau",
    ],
    "power bi": [
        "power bi",
        "powerbi",
    ],
    "excel": [
        "excel",
        "microsoft excel",
    ],
    "data analysis": [
        "data analysis",
        "data analytics",
        "data analysis techniques",
    ],
    "data visualization": [
        "data visualization",
        "data visualisation",
    ],
    "statistics": [
        "statistics",
        "statistical analysis",
    ],
    "cybersecurity": [
        "cybersecurity",
        "cyber security",
        "information security",
        "infosec",
    ],
    "network security": [
        "network security",
    ],
    "penetration testing": [
        "penetration testing",
        "penetration test",
        "pentesting",
        "pen testing",
    ],
    "vulnerability assessment": [
        "vulnerability assessment",
        "vulnerability analysis",
    ],
    "rest api": [
        "rest api",
        "rest apis",
        "restful api",
        "restful apis",
    ],
    "api development": [
        "api development",
        "api integration",
    ],
    "software testing": [
        "software testing",
        "software test",
    ],
    "automation testing": [
        "automation testing",
        "test automation",
        "automated testing",
    ],
    "selenium": [
        "selenium",
    ],
    "pytest": [
        "pytest",
    ],
    "junit": [
        "junit",
    ],
    "agile": [
        "agile",
        "agile methodology",
    ],
    "scrum": [
        "scrum",
    ],
    "figma": [
        "figma",
    ],
    "ui/ux": [
        "ui/ux",
        "ui ux",
        "user interface",
        "user experience",
    ],
}


# ============================================================
# TECHNICAL RELATIONSHIP KNOWLEDGE
# ============================================================
#
# IMPORTANT:
#
# These relationships NEVER mean the candidate explicitly used
# the related technology.
#
# They provide "related evidence" when the resume demonstrates
# a technical activity strongly associated with the technology.
#
# Example:
#
# CNN project
# -> deep learning
# -> image classification
#
# But:
#
# CNN != automatically TensorFlow
# CNN != automatically PyTorch
# CNN != automatically Keras
#
# Those remain related/unconfirmed unless the resume says so.
# ============================================================

TECHNICAL_RELATIONSHIPS = {

    # ---------------- MACHINE LEARNING ----------------

    "logistic regression": {
        "capabilities": [
            "machine learning",
            "classification",
            "predictive modeling",
            "statistical modeling",
        ],
        "related_tools": [
            "scikit-learn",
        ],
    },

    "linear regression": {
        "capabilities": [
            "machine learning",
            "regression",
            "predictive modeling",
            "statistical modeling",
        ],
        "related_tools": [
            "scikit-learn",
        ],
    },

    "decision tree": {
        "capabilities": [
            "machine learning",
            "classification",
            "regression",
            "predictive modeling",
        ],
        "related_tools": [
            "scikit-learn",
        ],
    },

    "random forest": {
        "capabilities": [
            "machine learning",
            "ensemble learning",
            "classification",
            "regression",
            "predictive modeling",
        ],
        "related_tools": [
            "scikit-learn",
        ],
    },

    "support vector machine": {
        "capabilities": [
            "machine learning",
            "classification",
            "regression",
            "predictive modeling",
        ],
        "related_tools": [
            "scikit-learn",
        ],
    },

    "svm": {
        "capabilities": [
            "machine learning",
            "classification",
            "regression",
            "predictive modeling",
        ],
        "related_tools": [
            "scikit-learn",
        ],
    },

    "k-means": {
        "capabilities": [
            "machine learning",
            "unsupervised learning",
            "clustering",
            "customer segmentation",
        ],
        "related_tools": [
            "scikit-learn",
        ],
    },

    "clustering": {
        "capabilities": [
            "machine learning",
            "unsupervised learning",
            "data analysis",
        ],
        "related_tools": [
            "scikit-learn",
        ],
    },

    "principal component analysis": {
        "capabilities": [
            "machine learning",
            "dimensionality reduction",
            "feature engineering",
            "data analysis",
        ],
        "related_tools": [
            "scikit-learn",
        ],
    },

    # ---------------- DEEP LEARNING ----------------

    "cnn": {
        "capabilities": [
            "deep learning",
            "computer vision",
            "image classification",
            "neural networks",
        ],
        "related_tools": [
            "tensorflow",
            "keras",
            "pytorch",
        ],
    },

    "convolutional neural network": {
        "capabilities": [
            "deep learning",
            "computer vision",
            "image classification",
            "neural networks",
        ],
        "related_tools": [
            "tensorflow",
            "keras",
            "pytorch",
        ],
    },

    "lstm": {
        "capabilities": [
            "deep learning",
            "sequence modeling",
            "time-series modeling",
            "recurrent neural networks",
        ],
        "related_tools": [
            "tensorflow",
            "keras",
            "pytorch",
        ],
    },

    "transformer": {
        "capabilities": [
            "deep learning",
            "sequence modeling",
            "attention mechanisms",
            "natural language processing",
        ],
        "related_tools": [
            "pytorch",
            "tensorflow",
        ],
    },

    "neural network": {
        "capabilities": [
            "deep learning",
            "machine learning",
            "neural networks",
        ],
        "related_tools": [
            "tensorflow",
            "keras",
            "pytorch",
        ],
    },

    # ---------------- COMPUTER VISION ----------------

    "image classification": {
        "capabilities": [
            "computer vision",
            "machine learning",
            "deep learning",
        ],
        "related_tools": [
            "opencv",
            "tensorflow",
            "keras",
            "pytorch",
        ],
    },

    "object detection": {
        "capabilities": [
            "computer vision",
            "image processing",
        ],
        "related_tools": [
            "opencv",
            "tensorflow",
            "pytorch",
        ],
    },

    "image processing": {
        "capabilities": [
            "computer vision",
            "image analysis",
        ],
        "related_tools": [
            "opencv",
        ],
    },

    # ---------------- DATA ----------------

    "data cleaning": {
        "capabilities": [
            "data preprocessing",
            "data analysis",
        ],
        "related_tools": [
            "pandas",
            "numpy",
        ],
    },

    "data preprocessing": {
        "capabilities": [
            "data preparation",
            "data analysis",
        ],
        "related_tools": [
            "pandas",
            "numpy",
        ],
    },

    "data visualization": {
        "capabilities": [
            "data analysis",
            "data reporting",
        ],
        "related_tools": [
            "matplotlib",
            "seaborn",
            "tableau",
            "power bi",
        ],
    },

    "statistical analysis": {
        "capabilities": [
            "statistics",
            "data analysis",
        ],
        "related_tools": [
            "numpy",
            "pandas",
        ],
    },

    # ---------------- WEB ----------------

    "responsive web design": {
        "capabilities": [
            "frontend development",
            "web development",
            "responsive design",
        ],
        "related_tools": [
            "html",
            "css",
            "javascript",
        ],
    },

    "frontend development": {
        "capabilities": ["web development", "user interface development"],
        "related_tools": ["react", "angular", "vue"],
    },

    "rest api": {
        "capabilities": [
            "backend development",
            "api development",
            "web services",
        ],
        "related_tools": [
            "node.js",
            "express.js",
            "django",
            "flask",
            "spring boot",
        ],
    },

    "database integration": {
        "capabilities": [
            "backend development",
            "database management",
            "application development",
        ],
        "related_tools": [
            "sql",
            "mysql",
            "postgresql",
            "mongodb",
        ],
    },

    # ---------------- CYBERSECURITY ----------------

    "vulnerability assessment": {
        "capabilities": [
            "cybersecurity",
            "security assessment",
            "vulnerability analysis",
        ],
        "related_tools": [],
    },

    "penetration testing": {
        "capabilities": [
            "cybersecurity",
            "security testing",
        ],
        "related_tools": [],
    },

    "network traffic analysis": {
        "capabilities": [
            "network security",
            "cybersecurity",
            "network analysis",
        ],
        "related_tools": [],
    },

    # ---------------- DEVOPS / CLOUD ----------------

    "containerization": {
        "capabilities": [
            "devops",
            "deployment",
        ],
        "related_tools": [
            "docker",
        ],
    },

    "continuous integration": {
        "capabilities": [
            "devops",
            "ci/cd",
        ],
        "related_tools": [
            "jenkins",
            "github",
        ],
    },

    "continuous deployment": {
        "capabilities": [
            "devops",
            "ci/cd",
        ],
        "related_tools": [],
    },
}


# ============================================================
# ACTION VERBS
# ============================================================

ACTION_VERBS = {
    "developed",
    "implemented",
    "designed",
    "built",
    "created",
    "engineered",
    "deployed",
    "configured",
    "integrated",
    "analyzed",
    "evaluated",
    "optimized",
    "automated",
    "tested",
    "trained",
    "processed",
    "visualized",
    "developed",
    "programmed",
    "maintained",
    "debugged",
    "validated",
    "predicted",
    "classified",
    "segmented",
    "detected",
    "managed",
    "led",
    "achieved",
    "implemented",
    "configured",
}


# ============================================================
# SECTION DETECTION
# ============================================================

SECTION_ALIASES = {
    "summary": [
        "summary",
        "professional summary",
        "career objective",
        "objective",
        "profile",
    ],
    "skills": [
        "skills",
        "technical skills",
        "core skills",
        "technical expertise",
        "competencies",
    ],
    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment",
        "internship",
        "internships",
        "work history",
    ],
    "projects": [
        "projects",
        "academic projects",
        "personal projects",
        "technical projects",
        "project experience",
    ],
    "education": [
        "education",
        "academic background",
        "educational qualification",
        "qualifications",
    ],
    "certifications": [
        "certifications",
        "certificates",
        "licenses",
    ],
    "achievements": [
        "achievements",
        "awards",
        "accomplishments",
    ],
}


def detect_sections(text: str) -> dict[str, str]:
    """
    Approximate section extraction from resume text.
    """

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    sections: dict[str, list[str]] = {}
    current = "general"
    sections[current] = []

    aliases = {}

    for section, names in SECTION_ALIASES.items():
        for name in names:
            aliases[normalize(name)] = section

    for line in lines:
        key = normalize(line).strip(":|- ")

        if key in aliases:
            current = aliases[key]
            sections.setdefault(current, [])
            continue

        sections.setdefault(current, []).append(line)

    return {
        key: "\n".join(value).strip()
        for key, value in sections.items()
        if value
    }


# ============================================================
# SKILL PARSING
# ============================================================

def split_skill_string(value: str) -> list[str]:
    """
    Handles:
        Python, SQL, React
        Python; SQL; React
        Python
        SQL
        React

    Also handles the older HireX problem where the recruiter
    entered:

        Python Machine Learning SQL NumPy Scikit-learn

    as one string.
    """

    if not value:
        return []

    value = value.strip()

    # First handle normal separators.
    parts = re.split(r"[,;|\n]+", value)

    result = []

    for part in parts:
        part = part.strip()

        if not part:
            continue

        # If it is already one known skill, retain it.
        n = normalize(part)

        if n in ALIASES:
            result.append(part)
            continue

        # Attempt longest known aliases first.
        known = []

        for canonical, aliases in ALIASES.items():
            for alias in aliases:
                if re.search(
                    rf"(?<!\w){re.escape(normalize(alias))}(?!\w)",
                    n,
                ):
                    known.append(
                        (
                            len(normalize(alias)),
                            canonical,
                            alias,
                        )
                    )

        if known and len(known) > 1:
            known.sort(reverse=True)

            consumed = set()

            for _, canonical, alias in known:
                if canonical not in consumed:
                    result.append(canonical)
                    consumed.add(canonical)

            # Remaining unknown text can still be useful.
            remaining = n

            for _, _, alias in known:
                remaining = re.sub(
                    rf"(?<!\w){re.escape(normalize(alias))}(?!\w)",
                    " ",
                    remaining,
                )

            remaining = re.sub(r"\s+", " ", remaining).strip()

            if remaining and len(remaining.split()) <= 5:
                result.append(remaining)
        else:
            result.append(part)

    return unique(result)


def parse_job_skills(job: Any) -> tuple[list[str], list[str]]:
    """
    Extract required and optional skills from the Job model.

    Supports:
        list
        newline-separated strings
        comma-separated strings
        old combined strings
    """

    required_raw = getattr(job, "required_skills", [])
    optional_raw = getattr(job, "optional_skills", [])

    def parse(value):
        if isinstance(value, list):
            output = []
            for item in value:
                output.extend(split_skill_string(str(item)))
            return unique(output)

        return split_skill_string(str(value or ""))

    return parse(required_raw), parse(optional_raw)


# ============================================================
# TERM MATCHING
# ============================================================

def contains_term(text: str, term: str) -> bool:
    """
    Safer matching than simple substring matching.
    """

    text_n = normalize(text)
    term_n = normalize(term)

    if not term_n:
        return False

    candidates = [term_n]
    for canonical, aliases in ALIASES.items():
        normalized_aliases = [normalize(canonical), *(normalize(a) for a in aliases)]
        if term_n in normalized_aliases:
            candidates.extend(normalized_aliases)
            break

    for candidate in unique(candidates):
        # A standalone C is valid, but C++ and C# are different languages.
        if candidate == "c":
            if re.search(r"(?<![a-z0-9])c(?![a-z0-9+#])", text_n):
                return True
            continue
        pattern = rf"(?<![a-z0-9]){re.escape(candidate)}(?![a-z0-9])"
        if re.search(pattern, text_n):
            return True
    return False


def occurrences(text: str, term: str) -> int:
    """
    Approximate occurrence count.
    """

    text_n = normalize(text)
    term_n = normalize(term)

    if not term_n:
        return 0

    try:
        return len(
            re.findall(
                rf"(?<!\w){re.escape(term_n)}(?!\w)",
                text_n,
            )
        )
    except re.error:
        return text_n.count(term_n)


# ============================================================
# SENTENCE EXTRACTION
# ============================================================

def sentences(text: str) -> list[str]:
    if not text:
        return []

    chunks = re.split(r"(?<=[.!?])\s+|\n+", text)

    return [
        s.strip(" •-\t")
        for s in chunks
        if len(s.strip()) >= 15
    ]


# ============================================================
# EXPLICIT SKILL EVIDENCE
# ============================================================

def explicit_skill_evidence(
    resume_text: str,
    skill: str,
    sections: dict[str, str],
) -> dict[str, Any]:

    matched_sections = []
    evidence_lines = []

    for section, content in sections.items():
        if contains_term(content, skill):
            matched_sections.append(section)

            for sentence in sentences(content):
                if contains_term(sentence, skill):
                    evidence_lines.append(sentence)

    # Fallback to whole resume.
    if not matched_sections and contains_term(resume_text, skill):
        matched_sections.append("general")

        for sentence in sentences(resume_text):
            if contains_term(sentence, skill):
                evidence_lines.append(sentence)

    evidence_lines = unique(evidence_lines)

    if evidence_lines:
        # Stronger when it appears in projects or experience,
        # because those sections demonstrate actual use.
        practical_sections = {
            "projects",
            "experience",
        }

        if practical_sections.intersection(matched_sections):
            level = "Explicit Practical Evidence"
            score = 100
        elif "skills" in matched_sections:
            level = "Explicit Skill Mention"
            score = 80
        else:
            level = "Explicit Evidence"
            score = 85

        return {
            "matched": True,
            "level": level,
            "score": score,
            "sections": matched_sections,
            "occurrences": occurrences(resume_text, skill),
            "evidence": evidence_lines[:8],
        }

    return {
        "matched": False,
        "level": "No Explicit Evidence",
        "score": 0,
        "sections": [],
        "occurrences": 0,
        "evidence": [],
    }


# ============================================================
# TECHNICAL RELATIONSHIP EVIDENCE
# ============================================================

def relationship_evidence(
    resume_text: str,
    skill: str,
    sections: dict[str, str] | None = None,
) -> dict[str, Any]:
    sections = sections or {"general": resume_text}
    skill_n = normalize(skill)

    capability_sources: list[str] = []
    related_sources: list[str] = []
    evidence: list[str] = []
    source_sections: list[str] = []

    for concept, relationship in TECHNICAL_RELATIONSHIPS.items():
        found_in = [
            section for section, content in sections.items()
            if contains_term(content, concept)
        ]
        if not found_in:
            continue
        capabilities = relationship.get("capabilities", [])
        tools = relationship.get("related_tools", [])

        if skill_n in [normalize(x) for x in capabilities]:
            capability_sources.append(concept)
            source_sections.extend(found_in)

        if skill_n in [normalize(x) for x in tools]:
            related_sources.append(concept)
            source_sections.extend(found_in)

        if skill_n in [normalize(x) for x in capabilities + tools]:
            for section in found_in:
                evidence.extend(
                    sentence for sentence in sentences(sections[section])
                    if contains_term(sentence, concept)
                )

    for technology, capabilities in TECHNOLOGY_CAPABILITIES.items():
        found_in = [section for section, content in sections.items() if contains_term(content, technology)]
        if found_in and skill_n in [normalize(item) for item in capabilities]:
            capability_sources.append(technology)
            source_sections.extend(found_in)
            evidence.extend(
                sentence for section in found_in for sentence in sentences(sections[section])
                if contains_term(sentence, technology)
            )

    # HTML/CSS/JavaScript implementation is evidence of web/frontend
    # capability, but it does not prove use of React, Angular, or Vue.
    if skill_n in {"react", "angular", "vue", "frontend development", "web development"}:
        for section, content in sections.items():
            if (
                contains_term(content, "html")
                and contains_term(content, "css")
                and contains_term(content, "javascript")
                and any(contains_term(content, term) for term in ("website", "web application", "web app", "e-commerce"))
            ):
                source_sections.append(section)
                if skill_n in {"frontend development", "web development"}:
                    capability_sources.append("frontend development")
                else:
                    related_sources.append("frontend development")
                evidence.extend(
                    sentence for sentence in sentences(content)
                    if any(contains_term(sentence, term) for term in ("html", "css", "javascript"))
                )

    capability_sources = unique(capability_sources)
    related_sources = unique(related_sources)
    source_sections = unique(source_sections)
    evidence = unique(evidence)

    if not capability_sources and not related_sources:
        return {"type": "none", "level": "No Related Evidence", "score": 0,
                "sources": [], "evidence": [], "sections": [],
                "related_capabilities": [], "reason": ""}

    related_capabilities = unique([
        capability
        for concept in capability_sources + related_sources
        for capability in (
            TECHNICAL_RELATIONSHIPS.get(concept, {}).get("capabilities", [])
            or TECHNOLOGY_CAPABILITIES.get(concept, [])
        )
        if normalize(capability) != skill_n
    ])

    if capability_sources:
        return {
            "type": "demonstrated_capability",
            "level": "Demonstrated Through Technical Work",
            "score": 82,
            "sources": capability_sources + related_sources,
            "evidence": evidence[:8],
            "sections": source_sections,
            "related_capabilities": related_capabilities,
            "reason": (
                f"The resume describes technical work that directly "
                f"demonstrates {skill}."
            ),
        }

    if related_sources:
        return {
            "type": "related_technology",
            "level": "Related Technical Evidence",
            "score": 60,
            "sources": related_sources,
            "evidence": evidence[:8],
            "sections": source_sections,
            "related_capabilities": related_capabilities,
            "reason": (
                f"The resume describes {', '.join(related_sources)}, "
                f"which is technically associated with {skill}. "
                f"However, the resume does not explicitly confirm that "
                f"{skill} was used."
            ),
        }

    return {"type": "none", "level": "No Related Evidence", "score": 0,
            "sources": [], "evidence": [], "sections": [],
            "related_capabilities": [], "reason": ""}


# ============================================================
# PROJECT / EXPERIENCE TECHNICAL EXTRACTION
# ============================================================

PROGRAMMING_LANGUAGES = [
    "Python", "Java", "JavaScript", "TypeScript", "C", "C++", "C#",
    "PHP", "Ruby", "Go", "Rust", "R", "Swift", "Kotlin", "SQL",
]
FRAMEWORKS = [
    "React", "Angular", "Vue", "Node.js", "Express.js", "Django", "Flask",
    "FastAPI", "Spring Boot", "ASP.NET", ".NET", "Next.js", "Laravel",
]
LIBRARIES = [
    "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "Pandas", "NumPy",
    "Matplotlib", "Seaborn", "OpenCV", "SciPy", "Spark", "jQuery",
]
DEVELOPMENT_TOOLS = [
    "Git", "GitHub", "Docker", "Kubernetes", "AWS", "Azure", "GCP",
    "Linux", "Jenkins", "Tableau", "Power BI", "Excel", "Figma", "Postman",
    "MATLAB", "Simulink", "AutoCAD", "SolidWorks", "ANSYS", "Arduino", "STM32",
]
TECHNOLOGY_CAPABILITIES = {
    "tensorflow": ["deep learning", "neural networks", "machine learning", "artificial intelligence"],
    "pytorch": ["deep learning", "neural networks", "machine learning", "artificial intelligence"],
    "keras": ["deep learning", "neural networks", "machine learning"],
    "scikit-learn": ["machine learning", "data science"],
    "pandas": ["data analysis", "data science", "python ecosystem"],
    "numpy": ["numerical computing", "data science", "python ecosystem"],
    "react": ["frontend development", "web development", "user interface development"],
    "angular": ["frontend development", "web development", "user interface development"],
    "vue": ["frontend development", "web development", "user interface development"],
    "fastapi": ["backend development", "python", "web api development"],
    "django": ["backend development", "python", "web development"],
    "flask": ["backend development", "python", "web api development"],
    "sql": ["database management", "data engineering", "software development"],
    "docker": ["containerization", "devops", "deployment"],
    "aws": ["cloud computing", "cloud deployment"],
    "azure": ["cloud computing", "cloud deployment"],
    "gcp": ["cloud computing", "cloud deployment"],
}
GENERIC_TECHNICAL_CONCEPTS = [
        "classification",
        "regression",
        "clustering",
        "segmentation",
        "prediction",
        "forecasting",
        "feature engineering",
        "feature extraction",
        "data preprocessing",
        "data cleaning",
        "model training",
        "model evaluation",
        "hyperparameter tuning",
        "cross validation",
        "image processing",
        "image classification",
        "object detection",
        "text classification",
        "sentiment analysis",
        "natural language processing",
        "database design",
        "database integration",
        "api development",
        "rest api",
        "authentication",
        "authorization",
        "responsive design",
        "frontend development",
        "backend development",
        "full stack development",
        "web development",
        "unit testing",
        "integration testing",
        "automation testing",
        "vulnerability assessment",
        "penetration testing",
        "network traffic analysis",
        "cloud deployment",
        "containerization",
        "continuous integration",
        "continuous deployment",
        "data visualization",
        "dashboard development",
        "neural networks",
        "predictive modeling",
        "unsupervised learning",
        "supervised learning",
        "customer segmentation",
        "model development",
        "model deployment",
        "data analysis",
        "web development",
        "frontend development",
        "backend development",
        "database management",
        "cloud computing",
        "cybersecurity",
        "embedded systems",
        "statistical analysis",
    ]

def _find_named_terms(text: str, candidates: list[str]) -> list[str]:
    return [term for term in candidates if contains_term(text, term)]

def extract_technical_concepts(text: str) -> dict[str, Any]:
    """Extract literal technologies separately from inferred capabilities."""
    normalized = normalize(text)
    models = _find_named_terms(normalized, list(TECHNICAL_RELATIONSHIPS))
    capabilities = []
    for concept in models:
        capabilities.extend(TECHNICAL_RELATIONSHIPS[concept].get("capabilities", []))
    methods = _find_named_terms(normalized, GENERIC_TECHNICAL_CONCEPTS)
    capabilities.extend(methods)
    languages = _find_named_terms(normalized, PROGRAMMING_LANGUAGES)
    frameworks = _find_named_terms(normalized, FRAMEWORKS)
    libraries = _find_named_terms(normalized, LIBRARIES)
    tools = _find_named_terms(normalized, DEVELOPMENT_TOOLS)
    for technology, derived in TECHNOLOGY_CAPABILITIES.items():
        if contains_term(normalized, technology):
            capabilities.extend(derived)
    if (
        contains_term(normalized, "html")
        and contains_term(normalized, "css")
        and contains_term(normalized, "javascript")
        and any(contains_term(normalized, term) for term in ("website", "web application", "web app", "e-commerce"))
    ):
        capabilities.extend(["frontend development", "web development", "user interface development"])
    return {
        "programming_languages": unique(languages),
        "frameworks": unique(frameworks),
        "libraries": unique(libraries),
        "tools": unique(tools),
        "models_and_algorithms": unique(models),
        "methods": unique(methods),
        "capabilities": unique(capabilities),
        "related_tools": unique([
            tool for model in models
            for tool in TECHNICAL_RELATIONSHIPS[model].get("related_tools", [])
            if not contains_term(normalized, tool)
        ]),
    }


def extract_project_records(project_text: str) -> list[dict[str, Any]]:
    """Split a Projects section into conservative, evidence-backed records."""
    lines = [line.strip() for line in (project_text or "").splitlines() if line.strip()]
    if not lines:
        return []

    action_starters = ACTION_VERBS | {
        "achieved", "used", "using", "applied", "leveraged", "responsible",
        "worked", "contributed", "resulted", "improved", "reduced", "increased", "wrote",
    }
    records: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    def flush() -> None:
        nonlocal current
        if current and current["lines"]:
            records.append(current)
        current = None

    for raw_line in lines:
        line = re.sub(r"^[\s•*\-]+", "", raw_line).strip()
        if not line:
            continue
        inline_title = re.match(r"^([^:]{3,90}):\s*(.+)$", line)
        if inline_title:
            title, body = inline_title.group(1).strip(), inline_title.group(2).strip()
            body_first = normalize(body.split()[0]).strip(":,;()[]{}") if body.split() else ""
            if body_first in action_starters:
                flush()
                current = {"name": title, "lines": [body]}
                continue
        project_prefix = re.match(r"(?i)^project\s*\d*\s*[:\-]\s*(.+)$", line)
        if project_prefix:
            flush()
            current = {"name": project_prefix.group(1).strip(), "lines": []}
            continue

        words = line.split()
        first = normalize(words[0]).strip(":,;()[]{}") if words else ""
        starts_with_action = first in action_starters
        looks_like_heading = (
            len(words) <= 10
            and len(line) <= 100
            and not re.search(r"[.!?]\s*$", line)
            and not re.search(r"\b\d+(?:\.\d+)?\s*(?:%|percent|accuracy)\b", line, re.I)
            and not starts_with_action
            and first not in {"the", "this", "these", "using", "based", "for", "in", "on"}
        )

        if looks_like_heading and (current is None or current["lines"]):
            flush()
            current = {"name": line.strip(" :.-"), "lines": []}
        else:
            if current is None:
                current = {"name": f"Project {len(records) + 1}", "lines": []}
            current["lines"].append(line)

    flush()
    if not records:
        return []

    metrics_pattern = re.compile(
        r"\b\d[\d,]*(?:\.\d+)?\s*(?:%|percent|accuracy|precision|recall|f1|"
        r"users|records|samples|datasets|ms|seconds|minutes|hours)\b|"
        r"\b(?:accuracy|precision|recall|f1|latency|throughput)\s*(?:of|at|:)?\s*\d[\d,.]*\s*%?",
        re.I,
    )
    domains = {
        "AI / Machine Learning": ["machine learning", "deep learning", "classification", "clustering", "neural networks", "predictive modeling"],
        "Data / Analytics": ["data analysis", "data visualization", "data cleaning", "customer segmentation", "statistical analysis"],
        "Web / Software Development": ["web development", "frontend development", "backend development", "api development", "database design", "responsive design"],
        "Cybersecurity": ["cybersecurity", "penetration testing", "vulnerability assessment", "network security"],
        "Cloud / DevOps": ["cloud computing", "cloud deployment", "containerization", "continuous integration", "continuous deployment"],
        "Embedded / Electronics": ["embedded systems", "microcontrollers", "digital electronics", "arduino", "stm32"],
    }
    application_terms = [
        "customer segmentation", "image classification", "handwritten digit recognition", "digit recognition",
        "object detection", "sentiment analysis", "fraud detection", "churn prediction",
        "e-commerce", "inventory management", "recommendation system", "traffic prediction",
    ]
    output = []
    for record in records:
        evidence = " ".join(record["lines"]).strip()
        full_text = f"{record['name']} {evidence}".strip()
        concepts = extract_technical_concepts(full_text)
        project_sentences = sentences(evidence)
        action_sentences = [
            sentence for sentence in project_sentences
            if any(re.search(rf"\b{re.escape(verb)}\b", normalize(sentence)) for verb in action_starters)
        ]
        result_sentences = [sentence for sentence in project_sentences if metrics_pattern.search(sentence)]
        detected_domains = [
            domain for domain, terms in domains.items()
            if any(contains_term(full_text, term) for term in terms)
        ]
        application_areas = _find_named_terms(full_text, application_terms)
        explicit_technologies = unique([
            item
            for category in ("programming_languages", "frameworks", "libraries", "tools")
            for item in concepts[category]
        ])
        output.append({
            "project_name": record["name"],
            "project_domain": detected_domains,
            "programming_languages": concepts["programming_languages"],
            "frameworks": concepts["frameworks"],
            "libraries": concepts["libraries"],
            "tools": concepts["tools"],
            "models_and_algorithms": concepts["models_and_algorithms"],
            "methods": concepts["methods"],
            "technical_concepts": concepts["capabilities"],
            "application_area": application_areas,
            "problem_solved": (action_sentences or project_sentences)[:2],
            "implementation_evidence": evidence,
            "action_statements": action_sentences,
            "results_metrics": result_sentences,
            "explicit_technologies": explicit_technologies,
            "related_tools": concepts["related_tools"],
        })
    return output


def extract_resume_knowledge(
    resume_text: str,
    sections: dict[str, str],
    projects: list[dict[str, Any]],
    required: list[str],
    optional: list[str],
) -> dict[str, Any]:
    concepts = extract_technical_concepts(resume_text)
    discovered = unique([
        item
        for category in ("programming_languages", "frameworks", "libraries", "tools", "models_and_algorithms", "methods")
        for item in concepts[category]
    ])
    requested = {normalize(item) for item in required + optional}
    additional = [item for item in discovered if normalize(item) not in requested]
    project_terms = unique([
        item
        for project in projects
        for category in ("programming_languages", "frameworks", "libraries", "tools", "models_and_algorithms", "methods", "technical_concepts")
        for item in project.get(category, [])
    ])
    capabilities = unique([
        item
        for project in projects
        for item in project.get("technical_concepts", [])
    ])
    evidence_blocks = [
        {
            "source_section": "Projects",
            "project_name": project["project_name"],
            "action": project["action_statements"],
            "implementation": project["implementation_evidence"],
            "results_metrics": project["results_metrics"],
            "models_and_methods": unique(project["models_and_algorithms"] + project["methods"]),
        }
        for project in projects
    ]
    for sentence in sentences(sections.get("experience", "")):
        n = normalize(sentence)
        has_action = any(re.search(rf"\b{re.escape(verb)}\b", n) for verb in ACTION_VERBS)
        has_technical = any(contains_term(sentence, term) for term in discovered)
        has_result = bool(re.search(r"\b\d[\d,.]*\s*(?:%|percent|users|records|ms|seconds)\b", sentence, re.I))
        if has_action and has_technical:
            evidence_blocks.append({
                "source_section": "Experience",
                "project_name": None,
                "action": [sentence],
                "implementation": sentence,
                "results_metrics": [sentence] if has_result else [],
                "models_and_methods": [],
            })
    return {
        "additional_skills_found": additional,
        "project_derived_skills": project_terms,
        "transferable_technical_capabilities": capabilities,
        "domain_knowledge": unique([domain for project in projects for domain in project["project_domain"]]),
        "project_analysis": projects,
        "technical_evidence": evidence_blocks,
    }


# ============================================================
# SKILL MATCH
# ============================================================

def skill_match(
    resume_text: str,
    skill: str,
    sections: dict[str, str],
) -> dict[str, Any]:

    explicit = explicit_skill_evidence(
        resume_text,
        skill,
        sections,
    )

    if explicit["matched"]:
        project_records = extract_project_records(sections.get("projects", ""))
        project_name = next((
            project["project_name"] for project in project_records
            if any(contains_term(line, skill) for line in sentences(project["implementation_evidence"]))
        ), None)
        return {
            "skill": skill,
            "matched": True,
            "exact_match": True,
            "match_type": "Explicit Match",
            "evidence_level": explicit["level"],
            "evidence_score": explicit["score"],
            "sections_found": explicit["sections"],
            "source_section": explicit["sections"][0] if explicit["sections"] else "general",
            "project_name": project_name,
            "related_capabilities": [],
            "occurrence_count": explicit["occurrences"],
            "detailed_evidence": explicit["evidence"],
            "reason": (
                f"{skill} is explicitly supported by the resume."
            ),
        }

    relationship = relationship_evidence(resume_text, skill, sections)

    if relationship["type"] != "none":
        project_records = extract_project_records(sections.get("projects", ""))
        sources = set(relationship["sources"])
        project_name = next((
            project["project_name"] for project in project_records
            if any(contains_term(project["implementation_evidence"], source) for source in sources)
            or any(
                normalize(project["implementation_evidence"]) in normalize(line)
                for line in relationship["evidence"]
            )
        ), None)
        return {
            "skill": skill,
            "matched": True,
            "exact_match": False,
            "match_type": "Related Match" if relationship["type"] == "related_technology" else "Demonstrated Match",
            "evidence_level": relationship["level"],
            "evidence_score": relationship["score"],
            "sections_found": relationship["sections"],
            "source_section": relationship["sections"][0] if relationship["sections"] else None,
            "project_name": project_name,
            "related_capabilities": relationship["related_capabilities"],
            "occurrence_count": 0,
            "detailed_evidence": relationship["evidence"],
            "reason": relationship["reason"],
        }

    return {
        "skill": skill,
        "matched": False,
        "exact_match": False,
        "match_type": "No Evidence",
        "evidence_level": "No Evidence",
        "evidence_score": 0,
        "sections_found": [],
        "source_section": None,
        "project_name": None,
        "related_capabilities": [],
        "occurrence_count": 0,
        "detailed_evidence": [],
        "reason": (
            f"No explicit or technically related evidence for "
            f"{skill} was found."
        ),
    }


# ============================================================
# JOB DESCRIPTION RELEVANCE
# ============================================================

STOP_WORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "that",
    "this",
    "are",
    "will",
    "you",
    "your",
    "our",
    "have",
    "has",
    "using",
    "use",
    "role",
    "job",
    "work",
    "candidate",
    "required",
    "preferred",
    "skills",
    "experience",
    "years",
}


def important_tokens(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#./-]{2,}", normalize(text))

    return {
        w
        for w in words
        if w not in STOP_WORDS
    }


def job_description_relevance(
    resume_text: str,
    job_description: str,
    required: list[str],
    optional: list[str],
    project_capabilities: list[str] | None = None,
) -> dict[str, Any]:

    jd_tokens = important_tokens(job_description)
    project_capabilities = project_capabilities or []
    resume_tokens = important_tokens(resume_text) | important_tokens(" ".join(project_capabilities))
    project_overlap = [
        capability for capability in project_capabilities
        if contains_term(job_description, capability)
    ]

    if not jd_tokens:
        token_score = 0
    else:
        overlap = jd_tokens.intersection(resume_tokens)
        token_score = min(
            100,
            round((len(overlap) / len(jd_tokens)) * 100),
        )

    skill_terms = required + optional

    matched_skill_count = 0

    for skill in skill_terms:
        if contains_term(resume_text, skill):
            matched_skill_count += 1

    if skill_terms:
        skill_score = (
            matched_skill_count / len(skill_terms)
        ) * 100
    else:
        skill_score = 0

    score = round(
        (token_score * 0.45) +
        (skill_score * 0.55)
    )

    return {
        "score": max(0, min(100, score)),
        "keyword_relevance": token_score,
        "skill_relevance": round(skill_score),
        "project_capability_overlap": unique(project_overlap),
        "reason": (
            "Measures job-description overlap using resume text and "
            "capabilities derived from documented project methods. "
            "Derived capabilities are not treated as explicit tool usage."
        ),
    }


# ============================================================
# REQUIRED / OPTIONAL SCORES
# ============================================================

def weighted_skill_score(results: list[dict[str, Any]]) -> int:

    if not results:
        return 0

    return round(
        sum(item["evidence_score"] for item in results)
        / len(results)
    )


# ============================================================
# EXPERIENCE SCORE
# ============================================================

def experience_score(
    resume_text: str,
    sections: dict[str, str],
) -> dict[str, Any]:

    content = (
        sections.get("experience", "")
        + "\n"
        + sections.get("projects", "")
    )

    if not content.strip():
        return {
            "score": 0,
            "reason": "No experience or project evidence detected.",
        }

    sentences_found = sentences(content)

    action_count = 0
    technical_count = 0
    result_count = 0

    for sentence in sentences_found:

        normalized = normalize(sentence)

        if any(
            re.search(rf"\b{re.escape(v)}\b", normalized)
            for v in ACTION_VERBS
        ):
            action_count += 1

        if re.search(
            r"\b(model|algorithm|framework|api|database|"
            r"application|system|website|dashboard|analysis|"
            r"dataset|classification|deployment|testing)\b",
            normalized,
        ):
            technical_count += 1

        if re.search(
            r"\b\d+(?:\.\d+)?\s*(%|percent|x|users|"
            r"records|datasets|projects|ms|seconds|minutes)\b",
            normalized,
        ):
            result_count += 1

    sentence_factor = min(100, len(sentences_found) * 10)
    action_factor = min(100, action_count * 20)
    technical_factor = min(100, technical_count * 15)
    result_factor = min(100, result_count * 25)

    score = round(
        sentence_factor * 0.20
        + action_factor * 0.25
        + technical_factor * 0.35
        + result_factor * 0.20
    )

    return {
        "score": max(0, min(100, score)),
        "action_sentences": action_count,
        "technical_sentences": technical_count,
        "measurable_results": result_count,
        "reason": (
            "Evaluates whether experience is expressed through "
            "specific actions, technical work and measurable outcomes."
        ),
    }


# ============================================================
# PROJECT SCORE
# ============================================================

def projects_score(
    sections: dict[str, str],
) -> dict[str, Any]:

    project_text = sections.get("projects", "")

    if not project_text:
        return {
            "score": 0,
            "projects_detected": 0,
            "technical_concepts": {},
            "projects": [],
            "project_derived_knowledge": {
                "models_and_algorithms": [], "methods": [], "capabilities": [],
                "programming_languages": [], "frameworks": [], "libraries": [], "tools": [],
            },
            "reason": "No Projects section detected.",
        }

    projects = extract_project_records(project_text)
    technical = extract_technical_concepts(project_text)

    project_scores = []
    for project in projects:
        exact_count = sum(len(project[key]) for key in (
            "programming_languages", "frameworks", "libraries", "tools", "models_and_algorithms", "methods"
        ))
        action_score = min(100, len(project["action_statements"]) * 45)
        technical_score = min(100, exact_count * 18 + len(project["technical_concepts"]) * 10)
        # A missing metric is not treated as fabrication or as a project failure.
        outcome_score = 70 if project["results_metrics"] else 45
        project["evidence_score"] = round(action_score * 0.30 + technical_score * 0.55 + outcome_score * 0.15)
        project_scores.append(project["evidence_score"])

    score = round(sum(project_scores) / len(project_scores)) if project_scores else 0
    project_count = len(projects)

    return {
        "score": score,
        "projects_detected": project_count,
        "technical_concepts": technical,
        "projects": projects,
        "project_derived_knowledge": {
            "models_and_algorithms": unique([x for p in projects for x in p["models_and_algorithms"]]),
            "methods": unique([x for p in projects for x in p["methods"]]),
            "capabilities": unique([x for p in projects for x in p["technical_concepts"]]),
            "programming_languages": unique([x for p in projects for x in p["programming_languages"]]),
            "frameworks": unique([x for p in projects for x in p["frameworks"]]),
            "libraries": unique([x for p in projects for x in p["libraries"]]),
            "tools": unique([x for p in projects for x in p["tools"]]),
        },
        "reason": (
            "Project evidence is scored per project from explicit technologies, "
            "models/methods, implementation actions and reported outcomes. "
            "Missing metrics do not invalidate technical work."
        ),
    }


# ============================================================
# CERTIFICATIONS
# ============================================================

def certifications_score(
    sections: dict[str, str],
) -> dict[str, Any]:

    text = sections.get("certifications", "")

    if not text:
        return {
            "score": 0,
            "certifications_detected": 0,
        }

    lines = [
        x.strip("•- ")
        for x in text.splitlines()
        if len(x.strip()) >= 5
    ]

    return {
        "score": min(100, len(lines) * 20),
        "certifications_detected": len(lines),
    }


# ============================================================
# RESUME QUALITY
# ============================================================

def resume_quality_score(
    resume_text: str,
    sections: dict[str, str],
) -> dict[str, Any]:

    checks = {}

    checks["summary"] = bool(sections.get("summary"))
    checks["skills"] = bool(sections.get("skills"))
    checks["experience"] = bool(sections.get("experience"))
    checks["projects"] = bool(sections.get("projects"))
    checks["education"] = bool(sections.get("education"))
    checks["certifications"] = bool(sections.get("certifications"))

    section_score = (
        sum(checks.values()) / len(checks)
    ) * 100

    text_length_score = min(
        100,
        max(
            20,
            round(len(resume_text) / 25),
        ),
    )

    score = round(
        section_score * 0.60
        + text_length_score * 0.40
    )

    return {
        "score": max(0, min(100, score)),
        "section_checks": checks,
        "reason": (
            "Evaluates resume structure, completeness and "
            "usable textual content."
        ),
    }


# ============================================================
# TECHNICAL EXPRESSION ANALYSIS
# ============================================================
#
# This is separate from keyword matching.
#
# Example:
#
# "Machine learning project"
#
# receives low expression quality.
#
# "Developed a K-Means clustering model to segment customers
# based on purchasing behavior."
#
# receives much stronger technical expression.
# ============================================================

def technical_expression_analysis(
    resume_text: str,
    sections: dict[str, str],
) -> dict[str, Any]:

    important_text = "\n".join(
        [
            sections.get("summary", ""),
            sections.get("experience", ""),
            sections.get("projects", ""),
        ]
    )

    sents = sentences(important_text)

    if not sents:
        return {
            "score": 0,
            "analysis": [],
        }

    analyses = []

    total = 0

    for sentence in sents:

        n = normalize(sentence)

        has_action = any(
            re.search(rf"\b{re.escape(v)}\b", n)
            for v in ACTION_VERBS
        )

        has_method = bool(
            re.search(
                r"\b(using|with|through|via|implemented|"
                r"developed|built|designed|trained|"
                r"integrated|applied)\b",
                n,
            )
        )

        has_technical_term = bool(
            re.search(
                r"\b(model|algorithm|api|database|"
                r"framework|dataset|classification|"
                r"clustering|dashboard|application|"
                r"system|automation|testing|"
                r"analysis|deployment|architecture)\b",
                n,
            )
        )

        has_result = bool(
            re.search(
                r"\b\d+(?:\.\d+)?\s*(%|percent|accuracy|"
                r"users|records|datasets|ms|seconds|minutes)\b",
                n,
            )
        )

        has_purpose = bool(
            re.search(
                r"\b(to|for|that|which|in order to|"
                r"aimed at|designed to)\b",
                n,
            )
        )

        score = 0

        if has_action:
            score += 25

        if has_method:
            score += 20

        if has_technical_term:
            score += 25

        if has_purpose:
            score += 15

        if has_result:
            score += 15

        score = min(100, score)
        starts_with_achievement = normalize(sentence).startswith(("achieved ", "reached ", "attained "))
        result_only = has_result and not (has_method or has_technical_term or has_purpose) and (
            not has_action or starts_with_achievement
        )
        if result_only:
            # A results sentence completes the preceding technical claim.
            score = max(score, 55)

        total += score

        if result_only:
            level = "Supporting Result Evidence"
        elif score < 40:
            level = "Weak Technical Expression"
        elif score < 70:
            level = "Moderate Technical Expression"
        else:
            level = "Strong Technical Expression"

        analyses.append(
            {
                "sentence": sentence,
                "score": score,
                "level": level,
                "has_action": has_action,
                "has_method": has_method,
                "has_technical_detail": has_technical_term,
                "has_purpose": has_purpose,
                "has_result": has_result,
                "supports_previous_technical_claim": result_only,
            }
        )

    average = round(total / len(analyses))

    return {
        "score": average,
        "analysis": analyses[:30],
        "reason": (
            "Evaluates whether technical work is expressed using "
            "clear actions, methods, technical details, purpose "
            "and measurable outcomes."
        ),
    }


# ============================================================
# EDUCATION ELIGIBILITY
# ============================================================
#
# IMPORTANT:
#
# Education has NO ATS SCORE.
#
# It is a separate eligibility result.
#
# Branch/stream is intentionally ignored.
# ============================================================

def extract_percentage(
    text: str,
    patterns: list[str],
) -> float | None:

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:
            try:
                value = float(match.group(1))

                if 0 <= value <= 100:
                    return value
            except ValueError:
                pass

    return None


def education_eligibility(
    sections: dict[str, str],
) -> dict[str, Any]:

    education_text = sections.get(
        "education",
        "",
    )

    if not education_text:
        return {
            "status": "Not Available",
            "eligible": None,
            "threshold": EDUCATION_THRESHOLD,
            "10th": None,
            "12th_or_intermediate": None,
            "degree": None,
            "checked_levels": [],
            "reason": (
                "Education section was not detected."
            ),
        }

    tenth = extract_percentage(
        education_text,
        [
            r"(?:10th|tenth|ssc)[^\d]{0,30}"
            r"(\d+(?:\.\d+)?)\s*%",
            r"(\d+(?:\.\d+)?)\s*%[^\n]{0,30}"
            r"(?:10th|tenth|ssc)",
        ],
    )

    intermediate = extract_percentage(
        education_text,
        [
            r"(?:12th|twelfth|intermediate|hsc|plus\s*two)"
            r"[^\d]{0,30}(\d+(?:\.\d+)?)\s*%",
            r"(\d+(?:\.\d+)?)\s*%[^\n]{0,30}"
            r"(?:12th|twelfth|intermediate|hsc)",
        ],
    )

    degree = extract_percentage(
        education_text,
        [
            r"(?:b\.?tech|bachelor|degree|b\.?e\.?|graduation)"
            r"[^\d]{0,60}(\d+(?:\.\d+)?)\s*%",
            r"(?:b\.?tech|bachelor|degree|b\.?e\.?|graduation)"
            r"[^\d]{0,60}"
            r"(?:cgpa|gpa)[^\d]{0,10}"
            r"(\d+(?:\.\d+)?)",
        ],
    )

    values = {
        "10th": tenth,
        "12th_or_intermediate": intermediate,
        "degree": degree,
    }

    available = {
        key: value
        for key, value in values.items()
        if value is not None
    }

    if not available:
        return {
            "status": "Not Available",
            "eligible": None,
            "threshold": EDUCATION_THRESHOLD,
            **values,
            "checked_levels": [],
            "reason": (
                "Academic percentages were not detected."
            ),
        }

    failed = [
        key
        for key, value in available.items()
        if value < EDUCATION_THRESHOLD
    ]

    if failed:
        status = "Not Qualified"
        eligible = False
        reason = (
            "One or more available academic percentages are "
            f"below the {EDUCATION_THRESHOLD}% requirement."
        )
    else:
        status = "Qualified"
        eligible = True
        reason = (
            "All available required academic percentages meet "
            f"the {EDUCATION_THRESHOLD}% threshold."
        )

    return {
        "status": status,
        "eligible": eligible,
        "threshold": EDUCATION_THRESHOLD,
        **values,
        "checked_levels": list(available.keys()),
        "reason": reason,
    }


# ============================================================
# STRENGTHS / WEAKNESSES
# ============================================================

def build_strengths(
    required_results: list[dict[str, Any]],
    optional_results: list[dict[str, Any]],
    project_result: dict[str, Any],
    expression_result: dict[str, Any],
    education_result: dict[str, Any],
) -> list[str]:

    strengths = []

    explicit_required = [
        x for x in required_results
        if x["evidence_level"] in {
            "Explicit Practical Evidence",
            "Explicit Evidence",
        }
    ]

    demonstrated_required = [
        x for x in required_results
        if "Demonstrated" in x["evidence_level"]
    ]

    if explicit_required:
        strengths.append(
            "Explicit required-skill evidence: "
            + ", ".join(x["skill"] for x in explicit_required[:8])
            + "."
        )

    if demonstrated_required:
        strengths.append(
            "Project/experience evidence demonstrates these required capabilities: "
            + ", ".join(x["skill"] for x in demonstrated_required[:8])
            + "."
        )

    concepts = project_result.get(
        "project_derived_knowledge",
        {},
    )

    models = concepts.get("models_and_algorithms", [])
    project_names = [p.get("project_name") for p in project_result.get("projects", [])]

    if models:
        strengths.append(
            "Project evidence identifies these models or algorithms: "
            + ", ".join(models[:8])
            + "."
        )

    if project_names:
        strengths.append("Analyzed project evidence from: " + ", ".join(project_names[:5]) + ".")

    measured_projects = [
        p["project_name"] for p in project_result.get("projects", [])
        if p.get("results_metrics")
    ]
    if measured_projects:
        strengths.append("Reported outcomes are present in: " + ", ".join(measured_projects[:5]) + ".")

    if expression_result.get("score", 0) >= 70:
        strengths.append(
            "Technical work is generally expressed with clear "
            "actions and technical details."
        )

    if education_result.get("eligible") is True:
        strengths.append(
            "Available academic percentages satisfy the separate "
            "education eligibility requirement."
        )

    return strengths


def build_weaknesses(
    required_results: list[dict[str, Any]],
    optional_results: list[dict[str, Any]],
    expression_result: dict[str, Any],
    education_result: dict[str, Any],
) -> list[str]:

    weaknesses = []

    missing_required = [
        x["skill"]
        for x in required_results
        if not x["matched"]
    ]

    related_required = [
        x["skill"]
        for x in required_results
        if x["evidence_level"]
        == "Related Technical Evidence"
    ]

    if missing_required:
        weaknesses.append(
            "Required skills without supporting resume evidence: "
            + ", ".join(missing_required)
            + "."
        )

    if related_required:
        weaknesses.append(
            "Some required technologies have related technical "
            "evidence, but their exact usage is not explicitly "
            "confirmed: "
            + ", ".join(related_required)
            + "."
        )

    if expression_result.get("score", 0) < 60:
        weaknesses.append(
            "Several technical statements could describe the "
            "candidate's actions, methods and results more clearly."
        )

    if education_result.get("eligible") is False:
        weaknesses.append(
            "The separate education eligibility check found one "
            "or more academic percentages below the required threshold."
        )

    return weaknesses


# ============================================================
# RECOMMENDATIONS
# ============================================================

def build_recommendations(
    required_results: list[dict[str, Any]],
    optional_results: list[dict[str, Any]],
    expression_result: dict[str, Any],
) -> list[dict[str, str]]:

    recommendations = []

    missing = [
        x["skill"]
        for x in required_results
        if not x["matched"]
    ]

    related = [
        x["skill"]
        for x in required_results
        if x["evidence_level"]
        == "Related Technical Evidence"
    ]

    if missing:
        recommendations.append(
            {
                "category": "High Priority",
                "recommendation": (
                    "If genuinely possessed, provide concrete "
                    "project or experience evidence for: "
                    + ", ".join(missing)
                    + ". Do not add technologies that were not used."
                ),
            }
        )

    if related:
        recommendations.append(
            {
                "category": "High Priority",
                "recommendation": (
                    "The resume provides related evidence for "
                    + ", ".join(related)
                    + ", but does not name those exact technologies. If actually used, identify the relevant "
                    "project and explicitly state the framework, library or tool. Do not add it otherwise."
                ),
            }
        )

    if expression_result.get("score", 0) < 70:
        recommendations.append(
            {
                "category": "Medium Priority",
                "recommendation": (
                    "Rewrite project and experience bullets using "
                    "Action + Technical Method + Purpose + Result. "
                    "For example: 'Developed X using Y to achieve Z.'"
                ),
            }
        )

    return recommendations


# ============================================================
# CORRECTIONS
# ============================================================

def build_corrections(
    sections: dict[str, str],
) -> list[dict[str, str]]:

    corrections = []

    important_sections = [
        ("projects", "project"),
        ("experience", "experience"),
        ("summary", "summary"),
    ]

    for section, label in important_sections:

        text = sections.get(section, "")

        if not text:
            continue

        for sentence in sentences(text):

            n = normalize(sentence)

            has_action = any(
                re.search(
                    rf"\b{re.escape(v)}\b",
                    n,
                )
                for v in ACTION_VERBS
            )

            has_result = bool(
                re.search(
                    r"\b\d+(?:\.\d+)?\s*(%|percent|accuracy|"
                    r"users|records|datasets)\b",
                    n,
                )
            )

            if not has_action:
                if has_result:
                    # A metric/result can be the supporting sentence for a nearby action.
                    continue
                corrections.append(
                    {
                        "section": label,
                        "original": sentence,
                        "suggestion": (
                            "Start with a clear action such as "
                            "Developed, Implemented, Designed, "
                            "Analyzed, Automated or Optimized."
                        ),
                    }
                )

            elif not has_result and len(sentence.split()) >= 8:
                corrections.append(
                    {
                        "section": label,
                        "original": sentence,
                        "suggestion": (
                            "Where applicable, add a measurable "
                            "result such as accuracy, performance "
                            "improvement, users, records processed "
                            "or response time."
                        ),
                    }
                )

            if len(corrections) >= 15:
                break

    return corrections


# ============================================================
# MISSING SKILLS
# ============================================================

def missing_skills(
    required_results: list[dict[str, Any]],
    optional_results: list[dict[str, Any]],
) -> dict[str, list[str]]:

    return {
        "critical": [
            x["skill"]
            for x in required_results
            if not x["matched"]
        ],
        "related": [
            x["skill"]
            for x in required_results
            if x.get("matched") and not x.get("exact_match", False)
        ],
        "optional": [
            x["skill"]
            for x in optional_results
            if not x["matched"]
        ],
    }


# ============================================================
# MAIN ANALYSIS
# ============================================================

def analyze(
    resume_text: str,
    job: Any,
) -> tuple[int, dict[str, Any]]:

    resume_text = resume_text or ""

    sections = detect_sections(resume_text)

    required, optional = parse_job_skills(job)

    job_description = getattr(
        job,
        "description",
        "",
    ) or ""

    # --------------------------------------------------------
    # Required skills
    # --------------------------------------------------------

    required_results = [
        skill_match(
            resume_text,
            skill,
            sections,
        )
        for skill in required
    ]

    optional_results = [
        skill_match(
            resume_text,
            skill,
            sections,
        )
        for skill in optional
    ]

    required_score = weighted_skill_score(
        required_results
    )

    optional_score = weighted_skill_score(
        optional_results
    )

    # Project-derived concepts are available to both project quality and
    # job-description relevance, while exact named technologies remain literal.
    projects = projects_score(sections)
    resume_knowledge = extract_resume_knowledge(
        resume_text, sections, projects.get("projects", []), required, optional
    )

    # --------------------------------------------------------
    # JD relevance
    # --------------------------------------------------------

    relevance = job_description_relevance(
        resume_text,
        job_description,
        required,
        optional,
        project_capabilities=resume_knowledge["transferable_technical_capabilities"],
    )

    semantic_score = relevance["score"]

    # --------------------------------------------------------
    # Experience
    # --------------------------------------------------------

    experience = experience_score(
        resume_text,
        sections,
    )

    # --------------------------------------------------------
    # Certifications
    # --------------------------------------------------------

    certifications = certifications_score(
        sections,
    )

    # --------------------------------------------------------
    # Resume quality
    # --------------------------------------------------------

    quality = resume_quality_score(
        resume_text,
        sections,
    )

    # --------------------------------------------------------
    # Technical expression
    # --------------------------------------------------------

    expression = technical_expression_analysis(
        resume_text,
        sections,
    )

    # --------------------------------------------------------
    # Education
    # --------------------------------------------------------
    #
    # ZERO contribution to ATS score.
    #

    education = education_eligibility(
        sections,
    )

    # --------------------------------------------------------
    # FINAL ATS SCORE
    # --------------------------------------------------------

    score = (
        required_score
        * WEIGHTS["required"]
        / 100
        +
        optional_score
        * WEIGHTS["optional"]
        / 100
        +
        semantic_score
        * WEIGHTS["semantic_relevance"]
        / 100
        +
        experience["score"]
        * WEIGHTS["experience"]
        / 100
        +
        projects["score"]
        * WEIGHTS["projects"]
        / 100
        +
        certifications["score"]
        * WEIGHTS["certifications"]
        / 100
        +
        quality["score"]
        * WEIGHTS["resume_quality"]
        / 100
        +
        expression["score"]
        * WEIGHTS["technical_expression"]
        / 100
    )

    total_score = round(
        max(0, min(100, score))
    )

    # --------------------------------------------------------
    # QUALIFICATION
    # --------------------------------------------------------

    minimum_score = int(
        getattr(
            job,
            "minimum_score",
            60,
        )
        or 60
    )

    all_required_supported = all(
        item["matched"]
        for item in required_results
    )

    if not required:
        all_required_supported = True

    if (
        total_score >= minimum_score
        and all_required_supported
    ):
        qualification_status = "QUALIFIED"
    else:
        qualification_status = "NOT QUALIFIED"

    # --------------------------------------------------------
    # Strengths / Weaknesses
    # --------------------------------------------------------

    strengths = build_strengths(
        required_results,
        optional_results,
        projects,
        expression,
        education,
    )

    weaknesses = build_weaknesses(
        required_results,
        optional_results,
        expression,
        education,
    )

    recommendations = build_recommendations(
        required_results,
        optional_results,
        expression,
    )

    for project in projects.get("projects", []):
        if not project["results_metrics"]:
            recommendations.append({
                "category": "Medium Priority",
                "recommendation": (
                    f"For '{project['project_name']}', add a verified outcome or metric if one is available; "
                    "do not estimate or invent a result."
                ),
            })
        if not project["action_statements"]:
            recommendations.append({
                "category": "Medium Priority",
                "recommendation": (
                    f"For '{project['project_name']}', clarify your actual implementation contribution "
                    "with an accurate action statement."
                ),
            })

    corrections = build_corrections(
        sections,
    )

    missing = missing_skills(
        required_results,
        optional_results,
    )

    section_evidence = []
    section_labels = {
        "summary": "Summary", "skills": "Skills", "experience": "Experience / Internships",
        "projects": "Projects", "certifications": "Certifications", "achievements": "Achievements",
    }
    for section_key, label in section_labels.items():
        section_text = sections.get(section_key, "")
        evidence_lines = []
        for sentence in sentences(section_text):
            concepts = extract_technical_concepts(sentence)
            has_technical_concept = any(
                concepts.get(category)
                for category in ("programming_languages", "frameworks", "libraries", "tools", "models_and_algorithms", "methods", "capabilities")
            )
            has_measurable_result = bool(re.search(r"\b\d[\d,.]*\s*(?:%|percent|users|records|samples|ms|seconds|minutes|hours)\b", sentence, re.I))
            has_action = any(re.search(rf"\b{re.escape(verb)}\b", normalize(sentence)) for verb in ACTION_VERBS)
            if has_technical_concept or (has_action and has_measurable_result):
                evidence_lines.append(sentence)
        section_evidence.append({
            "section": label,
            "evidence_count": len(evidence_lines),
            "evidence": evidence_lines,
        })

    project_capability_evidence = [
        {
            "capability": capability,
            "project_name": project.get("project_name"),
            "evidence_score": project.get("evidence_score", 0),
            "evidence": project.get("implementation_evidence", ""),
        }
        for project in projects.get("projects", [])
        for capability in project.get("technical_concepts", [])
    ]

    # --------------------------------------------------------
    # Detailed analysis
    # --------------------------------------------------------

    detail = {
        "ats_version": "2.0",

        "overall_score": total_score,

        "qualification_status": qualification_status,

        "minimum_required_score": minimum_score,

        # ----------------------------------------------------
        # SCORE BREAKDOWN
        # ----------------------------------------------------

        "scores": {
            "required": required_score,
            "optional": optional_score,
            "semantic_relevance": semantic_score,
            "experience": experience["score"],
            "projects": projects["score"],
            "certifications": certifications["score"],
            "resume_quality": quality["score"],
            "technical_expression": expression["score"],

            # Education deliberately excluded.
            "education": None,
        },

        "weights": WEIGHTS,

        # ----------------------------------------------------
        # REQUIRED SKILLS
        # ----------------------------------------------------

        "required_skills": required_results,

        # ----------------------------------------------------
        # OPTIONAL SKILLS
        # ----------------------------------------------------

        "optional_skills": optional_results,

        # ----------------------------------------------------
        # JOB DESCRIPTION RELEVANCE
        # ----------------------------------------------------

        "job_description_relevance": relevance,

        # ----------------------------------------------------
        # EXPERIENCE
        # ----------------------------------------------------

        "experience_analysis": experience,

        # ----------------------------------------------------
        # PROJECTS
        # ----------------------------------------------------

        "project_analysis": projects,

        # ----------------------------------------------------
        # CERTIFICATIONS
        # ----------------------------------------------------

        "certification_analysis": certifications,

        # ----------------------------------------------------
        # RESUME QUALITY
        # ----------------------------------------------------

        "resume_quality_analysis": quality,

        # ----------------------------------------------------
        # TECHNICAL EXPRESSION
        # ----------------------------------------------------

        "technical_expression": expression,

        # ----------------------------------------------------
        # EDUCATION
        # ----------------------------------------------------
        #
        # Separate from ATS score.
        #

        "education_eligibility": education,

        # ----------------------------------------------------
        # MISSING
        # ----------------------------------------------------

        "missing_skills": missing,

        # ----------------------------------------------------
        # QUALITATIVE ANALYSIS
        # ----------------------------------------------------

        "strengths": strengths,

        "weaknesses": weaknesses,

        "recommendations": recommendations,

        "corrections": corrections,

        # ----------------------------------------------------
        # DETECTED RESUME SECTIONS
        # ----------------------------------------------------

        "sections_detected": list(sections.keys()),

        # ----------------------------------------------------
        # PROJECT-DERIVED TECHNICAL KNOWLEDGE
        # ----------------------------------------------------

        "project_derived_knowledge": (
            projects.get("project_derived_knowledge", {})
        ),
        "job_context": {
            "title": getattr(job, "title", "") or "",
            "minimum_score": minimum_score,
            "required_skills": required,
            "preferred_skills": optional,
        },
        "resume_section_evidence": section_evidence,
        "project_capability_evidence": project_capability_evidence,
        "additional_skills_found": resume_knowledge["additional_skills_found"],
        "project_derived_skills": resume_knowledge["project_derived_skills"],
        "transferable_technical_capabilities": resume_knowledge["transferable_technical_capabilities"],
        "domain_knowledge": resume_knowledge["domain_knowledge"],
        "technical_evidence": resume_knowledge["technical_evidence"],
        "matched_skills": [x for x in required_results + optional_results if x.get("exact_match")],
        "related_skills": [x for x in required_results + optional_results if x.get("matched") and not x.get("exact_match")],
        "recommended_keywords": [
            {"keyword": x["skill"], "reason": x["reason"], "only_if_accurate": True}
            for x in required_results + optional_results
            if not x.get("exact_match")
        ],
    }

    return total_score, detail
