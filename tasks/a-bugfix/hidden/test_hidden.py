from datetime import date
from decimal import Decimal
import pytest
from ledger import Ledger, Entry, parse_amount, apply_discount, monthly_totals

def test_accounting_negative():
    assert parse_amount("(45.00)") == Decimal("-45.00")

def test_accounting_negative_with_minus_is_invalid():
    with pytest.raises(ValueError):
        parse_amount("-(45.00)")

def test_parse_currency_symbols():
    assert parse_amount("€ 3.10") == Decimal("3.10")
    assert parse_amount("-12") == Decimal("-12")

def test_between_inclusive():
    l = Ledger()
    l.add(Entry(date(2026, 1, 1), "a", Decimal("1")))
    l.add(Entry(date(2026, 1, 10), "a", Decimal("2")))
    l.add(Entry(date(2026, 1, 11), "a", Decimal("4")))
    got = l.between(date(2026, 1, 1), date(2026, 1, 10))
    assert sorted(e.amount for e in got) == [Decimal("1"), Decimal("2")]

def test_monthly_keys_padded_and_sorted():
    es = [Entry(date(2026, 11, 1), "a", Decimal("1")), Entry(date(2026, 3, 1), "a", Decimal("2")), Entry(date(2025, 12, 1), "a", Decimal("3"))]
    assert list(monthly_totals(es).keys()) == ["2025-12", "2026-03", "2026-11"]
    assert monthly_totals(es)["2026-03"] == Decimal("2")

def test_discount_half_up():
    assert apply_discount(Decimal("19.99"), Decimal("15")) == Decimal("16.99")

def test_existing_still_pass():
    assert parse_amount("1,234.50") == Decimal("1234.50")
    assert apply_discount(Decimal("100"), Decimal("10")) == Decimal("90.00")
