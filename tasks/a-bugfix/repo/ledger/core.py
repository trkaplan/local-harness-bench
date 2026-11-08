"""A tiny double-entry-ish ledger used by the finance team's scripts."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, ROUND_HALF_UP


@dataclass(frozen=True)
class Entry:
    day: date
    account: str
    amount: Decimal  # positive = credit, negative = debit
    memo: str = ""


def parse_amount(text: str) -> Decimal:
    """Parse amounts like '1,234.50', '-12', '(45.00)' (accounting negative), '€ 3.10'."""
    s = text.strip()
    negative = False
    if s.startswith("(") and s.endswith(")"):
        negative = True
        s = s[1:-1]
    s = s.replace(",", "").replace("€", "").replace("$", "").strip()
    if s.startswith("-"):
        negative = not negative
        s = s[1:]
    value = Decimal(s)
    return -value if negative else value


def apply_discount(amount: Decimal, percent: Decimal) -> Decimal:
    """Return amount reduced by percent, rounded to cents (half up)."""
    factor = (Decimal(100) - percent) / Decimal(100)
    return (amount * factor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@dataclass
class Ledger:
    entries: list[Entry] = field(default_factory=list)

    def add(self, entry: Entry) -> None:
        self.entries.append(entry)

    def balance(self, account: str | None = None) -> Decimal:
        total = Decimal(0)
        for e in self.entries:
            if account is None or e.account == account:
                total += e.amount
        return total

    def accounts(self) -> list[str]:
        return sorted({e.account for e in self.entries})

    def between(self, start: date, end: date) -> list[Entry]:
        """Entries with start <= day <= end (inclusive on both ends)."""
        return [e for e in self.entries if start <= e.day < end]


def monthly_totals(entries: list[Entry]) -> dict[str, Decimal]:
    """Map 'YYYY-MM' -> sum of amounts for that month, keys sorted ascending."""
    out: dict[str, Decimal] = {}
    for e in entries:
        key = f"{e.day.year}-{e.day.month}"
        out[key] = out.get(key, Decimal(0)) + e.amount
    return dict(sorted(out.items()))
