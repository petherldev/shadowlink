# ShadowLink
# Author: HErl (https://github.com/petherl/shadowlink.git)
# License: MIT

#!/usr/bin/env python3

import sys
import time
import pyshorteners
from urllib.parse import urlparse
import re

# Terminal Colors
R = "\033[31m"  # Red
G = "\033[32m"  # Green
Y = "\033[33m"  # Yellow
C = "\033[36m"  # Cyan
W = "\033[0m"  # White

# Meta Info
AUTHOR = "HErl"
GITHUB = "https://github.com/petherl"
VERSION = "0.0.1"

# Banner
BANNER = r"""

███████ ██   ██  █████  ██████   ██████  ██     ██     ██      ██ ███    ██ ██   ██ 
██      ██   ██ ██   ██ ██   ██ ██    ██ ██     ██     ██      ██ ████   ██ ██  ██  
███████ ███████ ███████ ██   ██ ██    ██ ██  █  ██     ██      ██ ██ ██  ██ █████   
     ██ ██   ██ ██   ██ ██   ██ ██    ██ ██ ███ ██     ██      ██ ██  ██ ██ ██  ██  
███████ ██   ██ ██   ██ ██████   ██████   ███ ███      ███████ ██ ██   ████ ██   ██ 
                                                                                    
           ✪ ShadowLink - Ultimate URL Cloaking Tool ✪
"""


def show_banner():
    print(f"{C}{BANNER}{W}")
    print(f"{G}➤ Version      : {W}{VERSION}")
    print(f"{G}➤ Author       : {W}{AUTHOR}")
    print(f"{G}➤ GitHub       : {W}{GITHUB}\n")


def loading_spinner():
    """Red circular loading spinner animation."""
    spinner = ["◐", "◓", "◑", "◒"]
    for _ in range(12):
        for frame in spinner:
            sys.stdout.write(
                f"\r{R}⟳ Please wait... generating your masked links {frame}{W}"
            )
            sys.stdout.flush()
            time.sleep(0.1)
    sys.stdout.write("\r\033[K")


def validate_url(url):
    return re.match(r"^(https?://)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(:\d{1,5})?(/.*)?$", url)


def validate_domain(domain):
    return re.match(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", domain)


def validate_keyword(keyword):
    return " " not in keyword and len(keyword) <= 15


def mask_url(domain, keyword, short_url):
    parsed = urlparse(short_url)
    return f"{parsed.scheme}://{domain}-{keyword}@{parsed.netloc}{parsed.path}"


def main():
    show_banner()

    try:
        while True:
            target_url = input(
                f"{Y}➤ Paste the original link to cloak {W}(e.g. https://example.com): {W}"
            )
            if validate_url(target_url):
                break
            print(
                f"{R}✖ That doesn't seem like a valid URL. Please double-check and try again.{W}"
            )

        while True:
            custom_domain = input(
                f"{Y}➤ Enter a domain to disguise as {W}(e.g. x.com): {W}"
            )
            if validate_domain(custom_domain):
                break
            print(
                f"{R}✖ Invalid domain format. Please provide a valid domain like facebook.com or gmail.com.{W}"
            )

        while True:
            keyword = input(f"{Y}➤ Choose a keyword to add (e.g. login, signup, verify): {W}")
            if validate_keyword(keyword):
                break
            print(
                f"{R}✖ Keyword should be under 15 characters and contain no spaces.{W}"
            )

        loading_spinner()

        shortener = pyshorteners.Shortener()
        services = [shortener.tinyurl, shortener.dagd, shortener.clckru, shortener.osdb]

        print(f"\n{C}➤ Original URL:{W} {target_url}\n")
        print(f"{G}[✓] Successfully generated masked URLs:\n")

        for idx, svc in enumerate(services):
            try:
                short = svc.short(target_url)
                masked = mask_url(custom_domain, keyword, short)
                print(f"{C}➤ Link {idx + 1}:{W} {masked}")
            except Exception as e:
                print(f"{R}✖ Failed to shorten with service {idx + 1}: {W}{str(e)}")

    except KeyboardInterrupt:
        print(f"\n{R}✖ Operation interrupted by user. Exiting...{W}")
    except Exception as e:
        print(f"{R}✖ Unexpected error occurred: {W}{str(e)}")


if __name__ == "__main__":
    main()
