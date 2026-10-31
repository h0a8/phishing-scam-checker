import csv
import sys
from urllib.parse import urlparse
import ipaddress

BAD_ENDINGS = (".xyz", ".top", ".xin", ".bond", ".tk", ".ml", ".ga", ".zip", ".mov", ".click", ".sbs", ".cf", ".gq", ".icu", ".buzz", ".rest", ".su", ".work")

KEYWORDS = ("login", "konto", "paket", "verify", "bestaeti", "verifizier", "sicherheit", "sperrung", "zahlung", "sendung", "gesperrt", "tracking", "zustellung", "signin", "account", "secure", "update", "confirm", "kostenlos", "gratis")

HOMOGLYPHS = {"\u0430": "a", "\u0435": "e", "\u043e": "o", "\u0440": "p", "\u0441": "c", "\u0445": "x", "\u0443": "y", "\u0456": "i"}

def main():
    url = input("Enter the URL: ")
    score, reasons = check_url(url)
    print(f"Score: {score}/100 -> {rating(score)}")

    if not reasons:
        print("Keine Auffälligkeiten gefunden")
    for reason in reasons:
        print(reason)


def get_domain(url):
    url = url.strip().lower()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return urlparse(url).hostname or ""


def has_ip(domain):
    try:
        ipaddress.ip_address(domain)
        return True
    except ValueError:
        return False 


def bad_ending(domain):
    return domain.endswith(BAD_ENDINGS)


def too_many_dots(domain):
    return domain.count(".") > 3


def find_keyword(url):
    url = url.lower()
    for word in KEYWORDS:
        if word in url:
            return word
    return None


def rating(score):
    if score >= 50:
        return "GEFÄHRLICH"
    elif score >= 25:
        return "VERDÄCHTIG"
    else:
        return "SICHER"


def check_url(url):
    domain = get_domain(url)
    if is_official(domain):
        return 0, ["Offizielle Domain"]
    score = 0
    reasons = []
    if has_ip(domain):
        score += 30
        reasons.append("+30 IP-Adresse statt Domain")

    if bad_ending(domain):
        score += 20
        reasons.append("+20 Verdächtige Endung")

    if too_many_dots(domain):
        score += 10
        reasons.append("+10 Zu viele Subdomains")

    if find_keyword(url):
        score += 10
        reasons.append(f'+10 Keyword "{find_keyword(url)}"')

    if find_brand_misuse(domain):
        score += 35
        reasons.append(f'+35 Markenname "{find_brand_misuse(domain)}" in fremder Domain')

    if find_lookalike(domain):
            score += 35
            reasons.append(f'+35 Domain ähnelt Marke "{find_lookalike(domain)}"')

    if has_punycode(domain):
        score += 25
        reasons.append("+25 Punycode-Domain (versteckte Sonderzeichen)")

    if has_foreign_chars(domain):
        score += 40
        reasons.append("+40 Fremde Schriftzeichen in der Domain")

    if find_keyword(url) and (bad_ending(domain) or find_brand_misuse(domain) or find_lookalike(domain)):
        score += 10
        reasons.append("+10 Kombination aus Keyword und verdächtiger Domain")

    return min(score, 100), reasons

def load_brands():
    brands = []
    with open("brands.csv", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            brands.append(row["domain"])
        return brands

def is_official(domain):
    for brand in load_brands():
        if domain == brand or domain.endswith("." + brand):
            return True
    return False


def has_punycode(domain):
    return "xn--" in domain

def has_foreign_chars(domain):
    for char in "äöüß":
        domain = domain.replace(char, "")
    return not domain.isascii()

def load_brand_keywords():
    keywords = []
    with open("brands.csv", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["keyword"] and row["keyword"] not in keywords:
                    keywords.append(row["keyword"])
    return keywords

def find_brand_misuse(domain):
    parts = domain.replace("-", ".").split(".")
    pairs = []
    for i in range(len(parts) - 1):
        pairs.append(parts[i] + parts[i + 1])

    for keyword in load_brand_keywords():
        if keyword in parts or keyword in pairs:
            return keyword
    return None

def distance(a, b):
    table = []
    for i in range(len(a) + 1):
        row = []
        for j in range(len(b) + 1):
            row.append(0)
        table.append(row)

    for i in range(len(a) + 1):
        table[i][0] = i
    for j in range(len(b) + 1):
        table[0][j] = j

    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                cost = 0
            else:
                cost = 1
            table[i][j] = min(table[i][j - 1] + 1, table[i - 1][j] + 1, table[i - 1][j - 1] + cost)
    return table[len(a)][len(b)]


def find_lookalike(domain):
    clean = ""
    for char in domain:
        if char in HOMOGLYPHS:
            clean += HOMOGLYPHS[char]
        else:
            clean += char

    parts = clean.replace("-", ".").split(".")
    keywords = load_brand_keywords()

    for part in parts:
        for keyword in keywords:
            if len(keyword) >= 5:
                d = distance(part, keyword)
                if len(keyword) >= 8:
                    max_d = 2
                else:
                    max_d = 1
                if d >= 1 and d <= max_d:
                    return keyword
                if d == 0 and clean != domain:
                    return keyword
    return None



if __name__ == "__main__":
    main()


