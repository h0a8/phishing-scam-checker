from project import get_domain, has_ip, bad_ending, too_many_dots, find_keyword, check_url, rating, is_official, has_punycode, has_foreign_chars, load_brands, load_brand_keywords, find_brand_misuse, distance, find_lookalike

def test_get_domain():
    assert get_domain("https://sparkasse.de") == "sparkasse.de"
    assert get_domain("HTTPS://SPARKASSE.DE") == "sparkasse.de"
    assert get_domain("   sparkasse.de/login ") == "sparkasse.de"
    assert get_domain("http://user@paypal.com:8080/a") == "paypal.com"
    assert get_domain("") == ""

def test_has_ip():
    assert has_ip("192.168.1.1") == True
    assert has_ip("::1") == True
    assert has_ip("256.1.1.1") == False
    assert has_ip("paypal.com") == False
    assert has_ip("") == False

def test_bad_ending():
    assert bad_ending("dhl-packet.xyz") == True
    assert bad_ending("free-iphone.tk") == True
    assert bad_ending("sparkasse.de") == False
    assert bad_ending("") == False


def test_too_many_dots():
    assert too_many_dots("a.e.i.o.u") == True
    assert too_many_dots("a.b.c.d") == False
    assert too_many_dots("www.sparkasse.de") == False
    assert too_many_dots("") == False

def test_find_keyword():
    assert find_keyword("https://sparkasse-konto.de") == "konto"
    assert find_keyword("dhl-paket.xyz/sendung") == "paket"
    assert find_keyword("paypal-login.de/konto") == "login"
    assert find_keyword("please-verify") == "verify"
    assert find_keyword("https://sparkasse.de") is None

def test_check_url():
    assert check_url("https://sparkasse.de") == (0, ["Offizielle Domain"])
    assert check_url("paypay.com/login") == (55, [
        '+10 Keyword "login"',
        '+35 Domain ähnelt Marke "paypal"',
        "+10 Kombination aus Keyword und verdächtiger Domain"])
    assert check_url("dhl.paket.xyz") == (75, [
        "+20 Verdächtige Endung",
        '+10 Keyword "paket"',
        '+35 Markenname "dhl" in fremder Domain',
        "+10 Kombination aus Keyword und verdächtiger Domain",])

    score, reasons = check_url("http://192.168.0.1/login")
    assert score == 40
    assert len(reasons) == 2

def test_rating():
    assert rating(0) == "SICHER"
    assert rating(24) == "SICHER"
    assert rating(25) == "VERDÄCHTIG"
    assert rating(49) == "VERDÄCHTIG"
    assert rating(50) == "GEFÄHRLICH"
    assert rating(100) == "GEFÄHRLICH"

def test_is_official():
    assert is_official("sparkasse.de") == True
    assert is_official("online.sparkasse.de") == True
    assert is_official("fakesparkasse.de") == False
    assert is_official("sparkasse.de.fake.xyz") == False

def test_has_punycode():
    assert has_punycode("xn--pypal-4ve.com") == True
    assert has_punycode("paypal.de") == False

def test_has_foreign_chars():
    assert has_foreign_chars("p\u0430ypal.de") == True
    assert has_foreign_chars("müller.de") == False
    assert has_foreign_chars("paypal.de") == False

def test_load_brands():
    brands = load_brands()
    assert "sparkasse.de" in brands
    assert "steampowered.com" in brands
    assert "" not in brands

def test_load_brand_keywords():
    keywords = load_brand_keywords()
    assert "sparkasse" in keywords
    assert "dhl" in keywords
    assert "" not in keywords
    assert len(keywords) == len(set(keywords))


def test_find_brand_misuse():
    assert find_brand_misuse("dhl-paket.xyz") == "dhl"
    assert find_brand_misuse("sparkasse.de.konto.xyz") == "sparkasse"
    assert find_brand_misuse("booking.com") is None
    assert find_brand_misuse("deutsche-bank-login.xyz") == "deutschebank"
    assert find_brand_misuse("lotto.de") is None


def test_distance():
    assert distance("kat", "kart") == 1
    assert distance("sparkase", "sparkasse") == 1
    assert distance("paypa1", "paypal") == 1
    assert distance("dhl", "dpd") == 2
    assert distance("abc", "abc") == 0
    assert distance("", "abc") == 3
    assert distance("abc", "") == 3


def test_find_lookalike():
    assert find_lookalike("sparkase.de") == "sparkasse"
    assert find_lookalike("paypa1-login.com") == "paypal"
    assert find_lookalike("p\u0430ypal.de") == "paypal"
    assert find_lookalike("wikipedia.org") is None
    assert find_lookalike("paypal-shop.de") is None
