"""Unit tests for shadowlink.shadowlink module."""

import re
import pytest
from shadowlink.shadowlink import (
    validate_url,
    validate_domain,
    validate_keyword,
    mask_url,
)


def test_validate_url_valid():
    assert validate_url("https://example.com")
    assert validate_url("http://site.org/path?query=123")


def test_validate_url_invalid():
    assert not validate_url("not_a_url")
    assert not validate_url("ftp://invalid.com")
    assert not validate_url("http:/missing-slash.com")


def test_validate_domain_valid():
    assert validate_domain("google.com")
    assert validate_domain("sub.domain.co.uk")


def test_validate_domain_invalid():
    assert not validate_domain("no-tld")
    assert not validate_domain("in valid.com")
    assert not validate_domain("domain.")


def test_validate_keyword_valid():
    assert validate_keyword("login")
    assert validate_keyword("verify123")


def test_validate_keyword_invalid():
    assert not validate_keyword("this has spaces")
    assert not validate_keyword("toolongkeywordfortest")  # >15 chars


def test_mask_url():
    short_url = "https://tinyurl.com/abc123"
    masked = mask_url("facebook.com", "login", short_url)
    assert masked.startswith("https://facebook.com-login@tinyurl.com/")
