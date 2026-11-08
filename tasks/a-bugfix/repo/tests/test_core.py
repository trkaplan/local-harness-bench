from datetime import date
from decimal import Decimal

from ledger import Ledger, Entry, parse_amount, apply_discount, monthly_totals


def test_parse_plain():
    assert parse_amount("12.50") == Decimal("12.50")


def test_parse_thousands():
    assert parse_amount("1,234.50") == Decimal("1234.50")


def test_balance_all():
    l = Ledger()
    l.add(Entry(date(2026, 1, 3), "cash", Decimal("100")))
    l.add(Entry(date(2026, 1, 4), "cash", Decimal("-40")))
    assert l.balance() == Decimal("60")


def test_discount_basic():
    assert apply_discount(Decimal("100"), Decimal("10")) == Decimal("90.00")
