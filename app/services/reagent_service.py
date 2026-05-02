"""Реагенты лаборатории (ДНК / РНК / катализатор) и перелив в Фонтан."""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Any

from app.config import get_settings
from app.db.models import User


@dataclass(frozen=True, slots=True)
class ReagentDrop:
    kind: str
    rarity: str
    dna: int
    rna: int
    cat: int
    note_key: str
    """Ключ для i18n Mini App (labSampleNote_*)."""


# Таблица дропа: kind хранится в lab_sample_collection; веса — целые, сумма = 100.
_DROP_TABLE: tuple[ReagentDrop, ...] = (
    # common
    ReagentDrop("saliva_trace", "common", 2, 0, 0, "saliva"),
    ReagentDrop("carrier_blood", "common", 2, 1, 0, "blood"),
    ReagentDrop("capsid_shard", "common", 1, 1, 0, "capsid"),
    ReagentDrop("envelope_snip", "common", 1, 0, 1, "envelope"),
    ReagentDrop("cytoplasm_soup", "common", 3, 0, 0, "cytosol"),
    ReagentDrop("surface_glycan", "common", 1, 2, 0, "glycan"),
    ReagentDrop("latent_signal", "common", 0, 2, 1, "latent"),
    ReagentDrop("vector_plasmid", "common", 2, 0, 1, "plasmid"),
    # rare
    ReagentDrop("spore_cluster", "rare", 3, 1, 0, "spore"),
    ReagentDrop("necrosis_tissue", "rare", 3, 0, 1, "necrosis"),
    ReagentDrop("lysogenic_plaque", "rare", 2, 2, 0, "lysogen"),
    ReagentDrop("reverse_transcript", "rare", 1, 2, 1, "retro"),
    ReagentDrop("interferon_stub", "rare", 0, 3, 1, "interferon"),
    ReagentDrop("nanoplex_tag", "rare", 2, 0, 2, "nanoplex"),
    # epic
    ReagentDrop("prion_misfold", "epic", 2, 2, 1, "prion"),
    ReagentDrop("immune_enzyme", "epic", 1, 3, 1, "enzyme"),
    ReagentDrop("strain_cipher", "epic", 4, 2, 1, "cipher"),
    ReagentDrop("symbiont_nexus", "epic", 2, 3, 1, "symbiont"),
)

_DROP_WEIGHTS: tuple[int, ...] = (
    # ~55% common / ~30% rare / ~15% epic
    8,
    7,
    7,
    7,
    7,
    6,
    6,
    7,
    5,
    5,
    5,
    5,
    5,
    5,
    4,
    4,
    4,
    3,
)


def roll_reagent_drop() -> ReagentDrop:
    return random.choices(_DROP_TABLE, weights=_DROP_WEIGHTS, k=1)[0]


def reset_fountain_pour_daily_if_needed(user: User) -> None:
    today = datetime.now(UTC).date()
    if user.fountain_pour_last_date != today:
        user.fountain_pour_units_today = 0
        user.fountain_pour_last_date = today


def apply_reagent_drop_to_user(user: User, drop: ReagentDrop) -> dict[str, Any]:
    """Начисляет реагенты и обновляет коллекцию образцов. Возвращает срез для API."""
    user.reagent_dna = int(user.reagent_dna) + drop.dna
    user.reagent_rna = int(user.reagent_rna) + drop.rna
    user.reagent_cat = int(user.reagent_cat) + drop.cat
    col: dict[str, Any] = dict(user.lab_sample_collection or {})
    col[drop.kind] = int(col.get(drop.kind, 0)) + 1
    user.lab_sample_collection = col
    return {
        "sample": {"kind": drop.kind, "rarity": drop.rarity, "note_key": drop.note_key},
        "reagents_gained": {"dna": drop.dna, "rna": drop.rna, "cat": drop.cat},
        "reagents_total": {
            "dna": user.reagent_dna,
            "rna": user.reagent_rna,
            "cat": user.reagent_cat,
        },
        "sample_collection": col,
    }


def contribution_weight(*, dna: int, rna: int, cat: int) -> float:
    s = get_settings()
    base = dna * float(s.reagent_weight_dna) + rna * float(s.reagent_weight_rna)
    mult = 1.0 + cat * float(s.reagent_cat_mult)
    return round(base * mult, 4)


def pour_units_remaining(user: User) -> int:
    reset_fountain_pour_daily_if_needed(user)
    cap = get_settings().fountain_pour_daily_unit_cap
    return max(0, cap - int(user.fountain_pour_units_today or 0))
