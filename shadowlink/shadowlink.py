#!/usr/bin/env python3

# ShadowLink
# Author: HErl (https://github.com/petherl/shadowlink.git)
# License: MIT


"""ShadowLink – Ultimate URL Cloaking Tool (CLI implementation).

Run `shadowlink` from the shell or `python -m shadowlink` and follow the
interactive prompts to produce convincing, cloaked links that mask the
real destination behind a trusted‑looking domain.
"""

from __future__ import annotations

import re
import sys
import time
from typing import Match, Optional
from urllib.parse import urlparse

import pyshorteners

# Terminal colours (ANSI escape sequences)
RED = "\033[31m"
GRN = "\033[32m"
YLW = "\033[33m"
CYN = "\033[36m"
RST = "\033[0m"

# Project metadata – pulled from the package root
from .version import __version__ as VERSION  # noqa: E402  (after imports)
AUTHOR = "HErl"
GITHUB = "https://github.com/petherl"

# ╭─ Banner – rendered once per run ───────────────────────────────────────╮
BANNER = r"""
███████ ██   ██  █████  ██████   ██████  ██     ██     ██      ██ ███    ██ ██   ██ 
██      ██   ██ ██   ██ ██   ██ ██    ██ ██     ██     ██      ██ ████   ██ ██  ██  
███████ ███████ ███████ ██   ██ ██    ██ ██  █  ██     ██      ██ ██ ██  ██ █████   
     ██ ██   ██ ██   ██ ██   ██ ██    ██ ██ ███ ██     ██      ██ ██  ██ ██ ██  ██  
███████ ██   ██ ██   ██ ██████   ██████   ███ ███      ███████ ██ ██   ████ ██   ██ 
                                                                                   
           ✪ ShadowLink – Ultimate URL Cloaking Tool ✪
"""
# ╰────────────────────────────────────────────────────────────────────────╯


def show_banner() -> None:
    """Print the stylised ASCII banner and project metadata."""
    print(f"{CYN}{BANNER}{RST}")
    print(f"{GRN}➤ Version      : {RST}{VERSION}")
    print(f"{GRN}➤ Author       : {RST}{AUTHOR}")
    print(f"{GRN}➤ GitHub       : {RST}{GITHUB}\n")


# ────────────────────────────── Helpers ──────────────────────────────────

def loading_spinner() -> None:
    """Display a small spinner while we contact shortening services."""
    spinner = ["◐", "◓", "◑", "◒"]
    for _ in range(12):
        for frame in spinner:
            sys.stdout.write(f"\r{RED}⟳ Please wait... generating your masked links {frame}{RST}")
            sys.stdout.flush()
            time.sleep(0.1)
    sys.stdout.write("\r\033[K")


_URL_RE = re.compile(r"^(https?://)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(:\d{1,5})?(/.*)?$")
_DOMAIN_RE = re.compile(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def validate_url(url: str) -> Optional[Match[str]]:
    """Return a regex match if *url* is a syntactically valid HTTP(S) URL."""
    return _URL_RE.match(url)


def validate_domain(domain: str) -> Optional[Match[str]]:
    """Return a regex match if *domain* looks like a hostname+TLD (e.g. x.com)."""
    return _DOMAIN_RE.match(domain)


def validate_keyword(keyword: str) -> bool:
    """Keyword must be ≤ 15 characters and contain no spaces."""
    return " " not in keyword and len(keyword) <= 15


def mask_url(domain: str, keyword: str, short_url: str) -> str:
    """Inject *domain* and *keyword* into *short_url* to form the disguised link."""
    parsed = urlparse(short_url)
    return f"{parsed.scheme}://{domain}-{keyword}@{parsed.netloc}{parsed.path}"


# ────────────────────────────── CLI logic ────────────────────────────────

def main() -> None:  # noqa: C901 (complexity fine for CLI script)
    """Interactive command‑line interface entry point."""

    show_banner()

    try:
        # 1. Target URL ----------------------------------------------------
        while True:
            target_url = input(
                f"{YLW}➤ Paste the original link to cloak {RST}(e.g. https://example.com): {RST}"
            )
            if validate_url(target_url):
                break
            print(f"{RED}✖ That doesn't seem like a valid URL. Please double‑check and try again.{RST}")

        # 2. Fake domain ---------------------------------------------------
        while True:
            custom_domain = input(f"{YLW}➤ Enter a domain to disguise as {RST}(e.g. x.com): {RST}")
            if validate_domain(custom_domain):
                break
            print(f"{RED}✖ Invalid domain format. Try something like facebook.com or gmail.com.{RST}")

        # 3. Keyword -------------------------------------------------------
        while True:
            keyword = input(f"{YLW}➤ Choose a keyword to add (e.g. login, signup, verify): {RST}")
            if validate_keyword(keyword):
                break
            print(f"{RED}✖ Keyword must be ≤ 15 chars with no spaces.{RST}")

        # 4. Shorten & cloak ----------------------------------------------
        loading_spinner()

        shortener = pyshorteners.Shortener()
        services = [shortener.tinyurl, shortener.dagd, shortener.clckru, shortener.osdb]

        print(f"\n{CYN}➤ Original URL:{RST} {target_url}\n")
        print(f"{GRN}[✓] Successfully generated masked URLs:\n")

        for idx, svc in enumerate(services, start=1):
            try:
                short = svc.short(target_url)
                masked = mask_url(custom_domain, keyword, short)
                print(f"{CYN}➤ Link {idx}:{RST} {masked}")
            except Exception as exc:  # pragma: no cover – network issues
                print(f"{RED}✖ Failed with service {idx}: {exc}{RST}")

    except KeyboardInterrupt:
        print(f"\n{RED}✖ Interrupted by user. Exiting...{RST}")
    except Exception as exc:  # pragma: no cover
        print(f"{RED}✖ Unexpected error: {exc}{RST}")

        