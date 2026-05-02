"""Группы ISO 3166-1 alpha-2 для фильтра рейтинга Mini App."""

from __future__ import annotations

# Европа (EU/EFTA/UK + западные кандидаты/микро)
EU_CODES: frozenset[str] = frozenset(
    """
    AT BE BG HR CY CZ DK EE FI FR DE GR HU IE IT LV LT LU MT NL PL PT RO SK SI ES SE
    GB IS NO CH LI MC AD SM VA BA AL MK ME RS XK
    """.split()
)

CIS_CODES: frozenset[str] = frozenset("RU BY UA MD AM AZ GE KZ KG TJ TM UZ".split())

ASIA_CODES: frozenset[str] = frozenset(
    """
    JP KR CN TW HK MO MN IN PK BD NP BT LK MV TH VN LA KH MM MY SG BN ID TL PH
    """.split()
)

MIDDLE_EAST_CODES: frozenset[str] = frozenset("SA AE QA KW BH OM YE JO LB SY IQ IR IL PS TR".split())

AFRICA_CODES: frozenset[str] = frozenset(
    """
    DZ AO BJ BW BF BI CV CM CF TD KM CG CD CI DJ EG GQ ER SZ ET GA GM GH GN GW KE LS
    LR LY MG MW ML MR MU MA MZ NA NE NG RW ST SN SL SO ZA SS SD TZ TG TN UG ZM ZW
    """.split()
)

AMERICAS_CODES: frozenset[str] = frozenset(
    """
    US CA MX GT BZ SV HN NI CR PA CU JM HT DO PR VI AR BO BR CL CO EC GY PY PE SR UY VE FK GS
    """.split()
)

OCEANIA_CODES: frozenset[str] = frozenset(
    """
    AU NZ FJ PG NC PF SB VU WS TO TV KI NR MP FM PW MH GU AS CK NU TK WF PN
    """.split()
)

VALID_TOP_SCOPES: frozenset[str] = frozenset(
    {"world", "country", "eu", "cis", "asia", "americas", "africa", "middle_east", "oceania"}
)


def normalize_top_scope(scope: str | None) -> str:
    s = (scope or "world").strip().lower()
    return s if s in VALID_TOP_SCOPES else "world"


def country_codes_for_top_scope(scope: str, *, user_country: str | None) -> list[str] | None:
    """None — без фильтра по стране (мир). Пустой список — нет подходящих кодов (пустой топ)."""
    s = normalize_top_scope(scope)
    if s == "world":
        return None
    if s == "country":
        if not user_country or len((c := user_country.strip())) != 2 or not c.isalpha():
            return []
        return [c.upper()]
    mapping: dict[str, frozenset[str]] = {
        "eu": EU_CODES,
        "cis": CIS_CODES,
        "asia": ASIA_CODES,
        "americas": AMERICAS_CODES,
        "africa": AFRICA_CODES,
        "middle_east": MIDDLE_EAST_CODES,
        "oceania": OCEANIA_CODES,
    }
    codes = mapping.get(s)
    if codes is None:
        return None
    return list(codes)
