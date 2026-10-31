# Phishing/Scam Checker

#### Video Demo: https://youtu.be/nii47hEEKhU

#### Description:
My Phishing/Scam Checker is a tool that checks a link for typical signs of phishing and scams and explains why it looks suspicious. It is built more specifically for the German market. The brand list focuses on mainly German companies that are often imitated by phishing and scam messages, and the bait words include mostly German bait words.
Many phishing and scams in Germany are done as an SMS or Email saying that a package could not be delivered or that a bank account was locked and the person has to log back in. The goal of this project is to give a quick and understandable second opinion on such a link for people who are maybe more prone to being a victim of such a scam. You paste the URL and the tool prints a score from 0 to 100, a rating and a list of reasons.

```
Enter the URL: dhl.paket.xyz
Score: 75/100 -> GEFÄHRLICH
+20 Verdächtige Endung
+10 Keyword "paket"
+35 Markenname "dhl" in fremder Domain
+10 Kombination aus Keyword und verdächtiger Domain
```

The tool's output is in German on purpose, because the target users are German speakers.


#### How it works:
First the domain is extracted from the URL (get_domain). Upper case, missing https://, ports and user@ prefixes are taken care of. If the domain belongs to a known brand (is_official), the check stops and returns 0 points. Otherwise every check that matches adds points and reasons:

| Check | Function | Points |
|-------|----------|--------|
| IP address instead of a domain name | has_ip | +30 |
| Suspicious ending domain | bad_ending | +20 |
| More than three dots | too_many_dots | +10 |
| Bait word in the URL | find_keyword | +10 |
| Real brand name inside foreign domain | find_brand_misuse | +35 |
| Domain that looks like a brand | find_lookalike | +35 |
| Punycode domain | has_punycode | +25 |
| Foreign characters, e.g. Cyrillic letters | has_foreign_chars | +40 |
| Bait word and (suspicious ending, brand misuse or lookalike) | check_url | +10 |

The score goes from 0 to 100, rating turns it into one of three levels:
- 0-24: SICHER
- 25-49: VERDÄCHTIG
- 50-100: GEFÄHRLICH

The points are weighted on how rarely a check happens on legitimate websites. Strong signals like Cyrillic letters or a faked brand name are enough on their own to make a link suspicious. Weak signals like bait words are never enough alone and only matter in combination.

#### Design Choices:
- **Official domains are checked first.** The real sparkasse.de/login should not get points for login, so known brand domains and their subdomains return 0. The check uses endswith("." + brand), so fakesparkasse.de and sparkasse.de.fake.xyz are not treated as an official link.

- **Brand names are compared as whole parts only.** The domain is split at dots and hyphens, and only complete parts are compared with the brand keywords. A substring search would find ing in booking.com, otto in lotto.de and bahn in autobahn.de. Very generic words (e.g. web from web.de or live from live.com) have no search keyword at all.

- **Neighbouring parts are joined into pairs.** Brands written as two words, like Deutsche Bank, are split into deutsche and Bank by the hyphen rule. To still detect deutsche-bank-login.xyz, every two neighbouring parts are also joined (deutschebank, banklogin,.....) and compared.

- **German umlauts are not foreign characters.** ä,ö,ü,ß are removed before the ASCII check, so a real German domain like müller.de does not get 40 points.

- **Own Levenshtein distance implemented.** distance(a, b) counts the minimum number of insertions, deletions and substitutions needed to turn one word into another, using the table method (Wagner Fischer algorithm) instead of a library, so I understand how lookalike detection works. (see Wikipedia: Levenshtein distance)

- **Strict lookalike rules.** Cyrillic letters that look like Latin ones (а, е, о, р …) are first translated back, so pаypal.de (with a Cyrillic "а") becomes paypal.de and is detected. Only keywords with 5+ letters are compared, and distance 2 is only allowed for keywords with 8+ letters, to keep false alarms low.

- **Brand list** brands.csv is intentionally a focused list of brands that are imitated often in Germany, not a list of every popular website. Comparing every domain against millions of real domains would give many false alarms back, because many legitimate domains are only one letter apart.

#### Files
 - project.py contains main and all check functions described above, + load_brands and load_brand_keywords, which read brands.csv with csv.DictReader.

- test_project.py contains pytest tests every function except main, including edge cases like the rating parametes (24/25, 49/50) and tricky domains like sparkasse.de.fake.xyz.

- brands.csv has three columns: name (display name), domain (official domain, used by is_official) and keyword (word searched for in foreign domains, empty for generic names)

- The tool only uses Python's standard library.


#### Limitations:
- **Regional Banks.** There are hundreds of regional banks with their own domains (e.g. sparkasse-rhein-neckar-nord.de). They are not recognised as official and are flagged as brand misuse. Since scammers use the same naming pattern (sparkasse-fake.de), the domain alone cannot reliably tell them apart.

- **False positives in lookalike detection.** Harmless domains that happen to resemble a brand are flagged, for example stream.de (Steam). A stricter rule would mean fewer false alarms but also fewer detected fakes.

- **Bait words.**  Words like update, account or secure also appear in many real URLS. This is why they only give 10 points.

- **Punycode vs umlauts.** müller.de gets 0 points, but the same domain written as xn--mller-kva.de gets 25 points for punycode.

- **Only the link is analysed.** The tool does not visit the website, redirections or checks URL shorteners. A shortened link to a phishing page will look safe.

- **Only some homoglyphs.** Only the most common Cyrillic lookalike letters are translated. Other scripts and tricks are not.


#### Responsible use:
My Phishing/Scam checker tool only analyses the text of a URL. It never opens the link. A low score does not prove that a link is safe, so it should be seen as a second opinion and not a guarantee.
