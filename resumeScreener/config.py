"""
Contains LLM settings and other configurations
"""

import os
# Agent Settings
AGENT_CONFIG = {
    "resume_parser": {
        "max_text_length": 5000,
        "skill_extraction": True
    },
    "jd_parser": {
        "max_text_length": 3000,
        "requirement_extraction": True
    },
    "matcher": {
        "min_match_threshold": 0.3,
        "max_missing_skills": 10
    },
    "advisor": {
        "max_suggestions": 5,
        "max_resources": 3
    }
}

# File Processing
FILE_CONFIG = {
    "supported_formats": [".pdf", ".docx", ".txt"]
}

# Judgeval Settings
JUDGEVAL_CONFIG = {
    "enabled": True,
    "log_level": "INFO",
    "metrics_enabled": True,
    "assertions_enabled": True
}