"""Base URL used in generated page metadata and sitemap entries."""

import os
from urllib.parse import urlsplit

DEFAULT_SITE_URL = "https://banan333.github.io/mirror-of-china/"
SITE_URL = os.environ.get("MIRROR_SITE_URL", DEFAULT_SITE_URL).rstrip("/") + "/"
parts = urlsplit(SITE_URL)
if (
    parts.scheme != "https" or not parts.hostname or parts.username or parts.password
    or any(char.isspace() or char in '<>&"\'?#' for char in SITE_URL)
):
    raise ValueError("MIRROR_SITE_URL must be an absolute HTTPS URL without credentials, query or fragment")
