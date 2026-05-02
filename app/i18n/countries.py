"""Отображение страны: флаг (региональные индикаторы) + локализованное имя."""

from __future__ import annotations

# Короткие обозначения; при отсутствии кода — эмоджи по умолчанию
_NAMES: dict[str, dict[str, str]] = {
    "ru": {
        "RU": "Россия",
        "UA": "Украина",
        "BY": "Беларусь",
        "KZ": "Казахстан",
        "KG": "Кыргызстан",
        "DE": "Германия",
        "FR": "Франция",
        "GB": "Великобритания",
        "US": "США",
        "ES": "Испания",
        "IT": "Италия",
        "PT": "Португалия",
        "BR": "Бразилия",
        "TR": "Турция",
        "PL": "Польша",
        "CN": "Китай",
        "TW": "Тайвань",
        "HK": "Гонконг",
        "MO": "Макао",
        "JP": "Япония",
        "KR": "Республика Корея",
        "SA": "Саудовская Аравия",
        "SG": "Сингапур",
        "NL": "Нидерланды",
        "BE": "Бельгия",
        "AT": "Австрия",
        "CH": "Швейцария",
        "SE": "Швеция",
        "NO": "Норвегия",
        "FI": "Финляндия",
        "CZ": "Чехия",
        "RO": "Румыния",
        "IL": "Израиль",
        "AE": "ОАЭ",
        "IN": "Индия",
        "ID": "Индонезия",
        "VN": "Вьетнам",
        "TH": "Таиланд",
        "MX": "Мексика",
        "AR": "Аргентина",
        "AU": "Австралия",
        "CA": "Канада",
    },
    "en": {
        "RU": "Russia",
        "UA": "Ukraine",
        "BY": "Belarus",
        "KZ": "Kazakhstan",
        "KG": "Kyrgyzstan",
        "DE": "Germany",
        "FR": "France",
        "GB": "United Kingdom",
        "US": "United States",
        "ES": "Spain",
        "IT": "Italy",
        "PT": "Portugal",
        "BR": "Brazil",
        "TR": "Turkey",
        "PL": "Poland",
        "CN": "China",
        "TW": "Taiwan",
        "HK": "Hong Kong",
        "MO": "Macau",
        "JP": "Japan",
        "KR": "South Korea",
        "SA": "Saudi Arabia",
        "SG": "Singapore",
        "NL": "Netherlands",
        "BE": "Belgium",
        "AT": "Austria",
        "CH": "Switzerland",
        "SE": "Sweden",
        "NO": "Norway",
        "FI": "Finland",
        "CZ": "Czechia",
        "RO": "Romania",
        "IL": "Israel",
        "AE": "United Arab Emirates",
        "IN": "India",
        "ID": "Indonesia",
        "VN": "Vietnam",
        "TH": "Thailand",
        "MX": "Mexico",
        "AR": "Argentina",
        "AU": "Australia",
        "CA": "Canada",
    },
}


def flag_emoji(iso3166_alpha2: str) -> str:
    c = iso3166_alpha2.strip().upper()
    if len(c) != 2 or not c.isalpha():
        return "🏳️"
    return chr(0x1F1E6 - ord("A") + ord(c[0])) + chr(0x1F1E6 - ord("A") + ord(c[1]))


def country_display(locale: str | None, country_code: str | None) -> str:
    if not country_code:
        return "—"
    code = country_code.strip().upper()
    loc = (locale or "ru").split("-")[0].lower()
    if loc in ("ru", "uk", "be", "kk", "ky"):
        bucket = _NAMES["ru"]
    elif loc == "en":
        bucket = _NAMES["en"]
    else:
        bucket = _NAMES["en"]
    name = bucket.get(code) or _NAMES["en"].get(code, code)
    return f"{flag_emoji(code)} {name}"
