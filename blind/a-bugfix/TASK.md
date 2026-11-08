The finance team reports three bugs in the `ledger` package. Fix them without changing public function names or signatures, and add a regression test for each in `tests/test_core.py`.

1. `parse_amount("(45.00)")` must return `Decimal("-45.00")` (accounting-style negative), and `parse_amount("-(45.00)")` is invalid input and must raise `ValueError`. Currently accounting negatives combined with a minus sign are mishandled.
2. `Ledger.between(start, end)` is documented as inclusive on both ends but currently excludes entries on `end`.
3. `monthly_totals` keys must be zero-padded `YYYY-MM` (for example `2026-03`, not `2026-3`), and must stay sorted ascending as strings.

Also `apply_discount(Decimal("19.99"), Decimal("15"))` must equal `Decimal("16.99")` (half-up rounding of 16.9915). Confirm this is already correct and keep it that way.

All existing tests must keep passing. Run the test suite before you finish.
