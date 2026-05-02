from __future__ import annotations

import math
import re
import secrets
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.models import InviteBoost, User
from app.services.clicker_network_regen import (
    effective_regen_bonus_bps,
    invite_temp_regen_bonus_bps,
    network_regen_bonus_bps,
    extend_invite_regen_boost_window,
)

UpgradeCode = Literal["viral_amplifier", "mutation_chance"]
BoostKind = Literal["strain_boost", "mutation_capsule"]
BOOST_KIND_STRAIN_BOOST: BoostKind = "strain_boost"

_ECONOMY_KEY = "economy_v1"
_BOOST_TOKEN_PREFIX = "b_"
_BOOST_TOKEN_BYTES = 18
_INVITE_BOOST_TTL_HOURS = 24
_DIRECT_INVITE_MAX_ENERGY_BONUS = 5
_LEGACY_REF = re.compile(r"^r(\d+)$")

_UPGRADE_MAX_LEVEL: dict[UpgradeCode, int] = {
    "viral_amplifier": 10,
    "mutation_chance": 10,
}

_UPGRADE_LABELS: dict[UpgradeCode, str] = {
    "viral_amplifier": "Вирусный усилитель",
    "mutation_chance": "Шанс мутации",
}

_BOOST_LABELS: dict[BoostKind, str] = {
    "strain_boost": "Усиленный штамм",
    "mutation_capsule": "Мутагенная капсула",
}


@dataclass(slots=True)
class InviteContext:
    inviter: User | None
    boost: InviteBoost | None = None


@dataclass(slots=True)
class InviteEconomyResult:
    bonus_hours: float
    base_hours: float
    multiplier: float
    viral_amplifier_level: int
    mutation_chance_level: int
    mutation_multiplier: int
    boost_label: str | None
    boosted: bool
    clicker_max_energy_bonus: int
    clicker_regen_bonus_bps: int
    got_timer_bonus: bool = True

    @property
    def total_seconds(self) -> int:
        return int(round(self.bonus_hours * 3600))

    @property
    def breakdown(self) -> dict[str, Any]:
        return {
            "bonus_hours": self.bonus_hours,
            "base_hours": self.base_hours,
            "total_seconds": self.total_seconds,
            "base_seconds": int(round(self.base_hours * 3600)),
            "multiplier": self.multiplier,
            "viral_amplifier_level": self.viral_amplifier_level,
            "mutation_chance_level": self.mutation_chance_level,
            "mutation_multiplier": self.mutation_multiplier,
            "boost_label": self.boost_label,
            "boosted": self.boosted,
            "clicker_max_energy_bonus": self.clicker_max_energy_bonus,
            "clicker_regen_bonus_bps": self.clicker_regen_bonus_bps,
        }

    def timer_reason(self, ref_label: str) -> str:
        if self.boosted or self.mutation_multiplier > 1 or self.viral_amplifier_level > 0:
            return f"усиленный реферал {ref_label}"
        return f"реферал {ref_label}"

    def notification_lines(self) -> list[str]:
        base_seconds = int(round(self.base_hours * 3600))
        total_seconds = int(round(self.bonus_hours * 3600))
        lines = [
            "🧬 Усиленный штамм сработал" if self.boosted or self.multiplier > 1 else "🧬 Новый носитель усилил штамм",
            f"+{_format_seconds_hms(total_seconds)} к таймеру",
            f"База: +{_format_seconds_hms(base_seconds)}",
        ]
        if self.viral_amplifier_level:
            lines.append(f"Вирусный усилитель L{self.viral_amplifier_level}: x{1 + 0.10 * self.viral_amplifier_level:.2f}")
        if self.boost_label:
            lines.append(f"{self.boost_label}: x{self.multiplier / max(1.0, 1 + 0.10 * self.viral_amplifier_level) / max(1, self.mutation_multiplier):.2f}")
        if self.mutation_multiplier > 1:
            lines.append(f"Мутация: x{self.mutation_multiplier}")
        lines.append(f"Кликер: +{self.clicker_max_energy_bonus} энергии к максимуму")
        if self.clicker_regen_bonus_bps:
            h = float(get_settings().invite_regen_boost_hours)
            lines.append(
                f"Реген (инвайт, окно до {h:g} ч от продления): +{self.clicker_regen_bonus_bps / 100:.2f}%"
            )
        return lines


class EconomyError(ValueError):
    pass


def _format_seconds_hms(seconds: int) -> str:
    seconds = max(0, int(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:d}:{m:02d}:{s:02d}"


def _economy_tree(user: User) -> dict[str, Any]:
    tree = dict(user.mutation_tree or {})
    data = dict(tree.get(_ECONOMY_KEY) or {})
    return data


def _set_economy_tree(user: User, data: dict[str, Any]) -> None:
    tree = dict(user.mutation_tree or {})
    tree[_ECONOMY_KEY] = data
    user.mutation_tree = tree


def upgrade_level(user: User, upgrade: UpgradeCode) -> int:
    return max(0, int(_economy_tree(user).get(upgrade) or 0))


def upgrade_cost(user: User, upgrade: UpgradeCode) -> dict[str, int] | None:
    level = upgrade_level(user, upgrade)
    if level >= _UPGRADE_MAX_LEVEL[upgrade]:
        return None
    nxt = level + 1
    if upgrade == "viral_amplifier":
        return {"dna": 80 * nxt, "rna": 5 * max(0, nxt - 2)}
    if upgrade == "mutation_chance":
        return {"dna": 120 * nxt, "rna": 10 * nxt}
    raise ValueError(f"unknown upgrade: {upgrade}")


def boost_cost(kind: BoostKind) -> dict[str, int]:
    if kind == "strain_boost":
        return {"dna": 100, "rna": 0}
    if kind == "mutation_capsule":
        return {"dna": 80, "rna": 10}
    raise ValueError(f"unknown boost kind: {kind}")


def _has_resources(user: User, cost: dict[str, int]) -> bool:
    return int(user.reagent_dna or 0) >= cost.get("dna", 0) and int(user.reagent_rna or 0) >= cost.get("rna", 0)


def _spend_resources(user: User, cost: dict[str, int]) -> None:
    if not _has_resources(user, cost):
        raise EconomyError("insufficient_reagents")
    user.reagent_dna = int(user.reagent_dna or 0) - cost.get("dna", 0)
    user.reagent_rna = int(user.reagent_rna or 0) - cost.get("rna", 0)


async def buy_upgrade(session: AsyncSession, user: User, upgrade: UpgradeCode) -> dict[str, Any]:
    cost = upgrade_cost(user, upgrade)
    if cost is None:
        raise EconomyError("upgrade_max_level")
    _spend_resources(user, cost)
    data = _economy_tree(user)
    data[upgrade] = upgrade_level(user, upgrade) + 1
    _set_economy_tree(user, data)
    await session.flush()
    return economy_state_payload(user, datetime.now(UTC))


async def purchase_upgrade(session: AsyncSession, user: User, upgrade: str) -> dict[str, Any]:
    if upgrade not in _UPGRADE_MAX_LEVEL:
        raise EconomyError("unknown_upgrade")
    return await buy_upgrade(session, user, upgrade)  # type: ignore[arg-type]


async def create_invite_boost(
    session: AsyncSession,
    user: User,
    *,
    kind: BoostKind,
) -> InviteBoost:
    if kind not in _BOOST_LABELS:
        raise EconomyError("unknown_boost")
    cost = boost_cost(kind)
    _spend_resources(user, cost)
    now = datetime.now(UTC)
    boost = InviteBoost(
        id=uuid.uuid4(),
        owner_user_id=user.id,
        token=await _allocate_unique_boost_token(session),
        kind=kind,
        dna_spent=cost.get("dna", 0),
        rna_spent=cost.get("rna", 0),
        bonus_multiplier=1.5 if kind == "strain_boost" else 1.0,
        mutation_bonus_chance=0.0 if kind == "strain_boost" else 0.10,
        max_uses=1,
        uses=0,
        expires_at=now + timedelta(hours=_INVITE_BOOST_TTL_HOURS),
    )
    session.add(boost)
    await session.flush()
    return boost


def build_economy_state(user: User, now: datetime | None = None) -> dict[str, Any]:
    return economy_state_payload(user, now)


async def _allocate_unique_boost_token(session: AsyncSession) -> str:
    for _ in range(24):
        token = secrets.token_urlsafe(_BOOST_TOKEN_BYTES).rstrip("=")
        exists = await session.scalar(select(InviteBoost.id).where(InviteBoost.token == token))
        if exists is None:
            return token
    raise RuntimeError("invite_boost token allocation failed")


def is_boost_payload(payload: str | None) -> bool:
    return bool(payload and payload.startswith(_BOOST_TOKEN_PREFIX) and len(payload) > len(_BOOST_TOKEN_PREFIX))


async def resolve_invite_context(session: AsyncSession, start_arg: str | None) -> InviteContext:
    arg = (start_arg or "").strip()
    if is_boost_payload(arg):
        token = arg[len(_BOOST_TOKEN_PREFIX):]
        now = datetime.now(UTC)
        boost = await session.scalar(
            select(InviteBoost)
            .where(
                InviteBoost.token == token,
                InviteBoost.expires_at > now,
                InviteBoost.uses < InviteBoost.max_uses,
            )
            .with_for_update()
        )
        if boost is None:
            return InviteContext(inviter=None)
        inviter = await session.get(User, boost.owner_user_id)
        return InviteContext(inviter=inviter, boost=boost)
    if not arg:
        return InviteContext(inviter=None)
    m = _LEGACY_REF.match(arg)
    if m:
        tid = int(m.group(1))
        if tid <= 0:
            return InviteContext(inviter=None)
        return InviteContext(inviter=await session.scalar(select(User).where(User.telegram_id == tid)))
    return InviteContext(inviter=await session.scalar(select(User).where(User.referral_token == arg)))


def boost_payload(boost: InviteBoost) -> str:
    return f"{_BOOST_TOKEN_PREFIX}{boost.token}"


def _mutation_multiplier(user: User, boost: InviteBoost | None) -> int:
    level = upgrade_level(user, "mutation_chance")
    x3_chance = 0.005 + 0.005 * math.floor(level / 2)
    x2_chance = 0.03 + 0.02 * level
    if boost is not None:
        x2_chance += float(boost.mutation_bonus_chance or 0.0)
    roll = secrets.randbelow(10_000) / 10_000
    if roll < x3_chance:
        return 3
    if roll < x3_chance + x2_chance:
        return 2
    return 1


def calculate_invite_economy(inviter: User, boost: InviteBoost | None = None) -> InviteEconomyResult:
    settings = get_settings()
    base_hours = float(settings.bonus_hours_per_referral)
    viral_level = upgrade_level(inviter, "viral_amplifier")
    mutation_level = upgrade_level(inviter, "mutation_chance")
    amp_mult = 1.0 + 0.10 * viral_level
    boost_mult = float(boost.bonus_multiplier) if boost is not None else 1.0
    mutation_mult = _mutation_multiplier(inviter, boost)
    multiplier = amp_mult * boost_mult * mutation_mult
    return InviteEconomyResult(
        bonus_hours=base_hours * multiplier,
        base_hours=base_hours,
        multiplier=multiplier,
        viral_amplifier_level=viral_level,
        mutation_chance_level=mutation_level,
        mutation_multiplier=mutation_mult,
        boost_label=_BOOST_LABELS.get(boost.kind) if boost is not None else None,
        boosted=boost is not None,
        clicker_max_energy_bonus=_DIRECT_INVITE_MAX_ENERGY_BONUS,
        clicker_regen_bonus_bps=int(get_settings().invite_regen_boost_bps),
    )


def apply_invite_economy(
    inviter: User,
    *,
    base_bonus_hours: float,
    invite_context: InviteContext | None = None,
) -> InviteEconomyResult:
    result = calculate_invite_economy(inviter, invite_context.boost if invite_context else None)
    # Keep the explicit argument in the public function contract for callers/tests that
    # want to simulate a different balance without mutating Settings.
    if abs(result.base_hours - base_bonus_hours) > 0.0001:
        multiplier = result.multiplier
        result = InviteEconomyResult(
            bonus_hours=float(base_bonus_hours) * multiplier,
            base_hours=float(base_bonus_hours),
            multiplier=multiplier,
            viral_amplifier_level=result.viral_amplifier_level,
            mutation_chance_level=result.mutation_chance_level,
            mutation_multiplier=result.mutation_multiplier,
            boost_label=result.boost_label,
            boosted=result.boosted,
            clicker_max_energy_bonus=result.clicker_max_energy_bonus,
            clicker_regen_bonus_bps=result.clicker_regen_bonus_bps,
        )
    apply_invite_clicker_growth(inviter, result)
    consume_boost(invite_context.boost if invite_context else None)
    return result


def apply_invite_clicker_growth(inviter: User, result: InviteEconomyResult) -> None:
    inviter.clicker_max_energy_bonus = int(inviter.clicker_max_energy_bonus or 0) + result.clicker_max_energy_bonus
    extend_invite_regen_boost_window(inviter)


def consume_boost(boost: InviteBoost | None) -> None:
    if boost is not None:
        boost.uses = int(boost.uses or 0) + 1


def economy_state_payload(user: User, now: datetime | None = None) -> dict[str, Any]:
    if now is None:
        now = datetime.now(UTC)
    upgrades = {}
    for code in ("viral_amplifier", "mutation_chance"):
        lvl = upgrade_level(user, code)  # type: ignore[arg-type]
        cost = upgrade_cost(user, code)  # type: ignore[arg-type]
        upgrades[code] = {
            "code": code,
            "label": _UPGRADE_LABELS[code],  # type: ignore[index]
            "level": lvl,
            "max_level": _UPGRADE_MAX_LEVEL[code],  # type: ignore[index]
            "next_cost": cost,
        }
    base_hours = float(get_settings().bonus_hours_per_referral)
    amp_mult = 1.0 + 0.10 * upgrade_level(user, "viral_amplifier")
    x2 = 0.03 + 0.02 * upgrade_level(user, "mutation_chance")
    x3 = 0.005 + 0.005 * math.floor(upgrade_level(user, "mutation_chance") / 2)
    return {
        "reagents": {
            "dna": int(user.reagent_dna or 0),
            "rna": int(user.reagent_rna or 0),
            "cat": int(user.reagent_cat or 0),
        },
        "upgrades": upgrades,
        "boosts": {
            "strain_boost": {
                "kind": "strain_boost",
                "label": _BOOST_LABELS["strain_boost"],
                "cost": boost_cost("strain_boost"),
                "multiplier": 1.5,
                "ttl_hours": _INVITE_BOOST_TTL_HOURS,
            },
            "mutation_capsule": {
                "kind": "mutation_capsule",
                "label": _BOOST_LABELS["mutation_capsule"],
                "cost": boost_cost("mutation_capsule"),
                "mutation_bonus_chance": 0.10,
                "ttl_hours": _INVITE_BOOST_TTL_HOURS,
            },
        },
        "forecast": {
            "base_bonus_hours": base_hours,
            "viral_multiplier": round(amp_mult, 3),
            "expected_direct_bonus_hours": round(base_hours * amp_mult, 3),
            "mutation_x2_chance": round(x2, 4),
            "mutation_x3_chance": round(x3, 4),
        },
        "clicker_growth": {
            "max_energy_bonus": int(user.clicker_max_energy_bonus or 0),
            "regen_bonus_bps": effective_regen_bonus_bps(user, now),
            "network_regen_bonus_bps": network_regen_bonus_bps(user),
            "invite_temp_regen_bonus_bps": invite_temp_regen_bonus_bps(user, now),
            "invite_regen_boost_ends_at": (
                user.invite_regen_boost_ends_at.isoformat()
                if user.invite_regen_boost_ends_at
                else None
            ),
            "mini_regen_online_direct": int(user.mini_regen_online_direct or 0),
            "mini_regen_online_subtree": int(user.mini_regen_online_subtree or 0),
            "next_direct_invite_max_energy": _DIRECT_INVITE_MAX_ENERGY_BONUS,
            "next_direct_invite_regen_bps": int(get_settings().invite_regen_boost_bps),
            "next_direct_invite_regen_hours": float(get_settings().invite_regen_boost_hours),
        },
    }
