import sys, os, pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import api._lib.misconceptions as M

# ---------- g5-decimal-ops ----------
class TestDecimalOps:
    P_ADD = {"a": 3.5, "b": 1.25, "op": "+"}
    P_SUB = {"a": 5.4, "b": 2.18, "op": "-"}

    def test_ignored_the_decimal_point_add(self):
        # 35 + 125 = 160 -> 1.60 = 1.6 (correct is 4.75)
        assert M.ignored_the_decimal_point(self.P_ADD) == "1.6"

    def test_ignored_the_decimal_point_sub(self):
        # 541 - 28 = 513 -> 5.13 (correct is 2.61)
        p = {"a": 5.41, "b": 2.8, "op": "-"}
        assert M.ignored_the_decimal_point(p) == "5.13"

    def test_ignored_the_decimal_point_applies_negative(self):
        # 54 - 218 < 0 -> should not apply
        assert not M.ignored_the_decimal_point_applies({"a": 5.4, "b": 2.18, "op": "-"})

    def test_subtracted_smaller_digit_from_larger(self):
        # 5.40 - 2.18 -> |5-2|.|4-1||0-8| = 3.38 (correct is 3.22)
        assert M.subtracted_smaller_digit_from_larger(self.P_SUB) == "3.38"

    def test_subtracted_smaller_digit_from_larger_applies(self):
        assert M.subtracted_smaller_digit_from_larger_applies(self.P_SUB)
        # no regrouping needed: 5.4 - 2.1 -> False
        assert not M.subtracted_smaller_digit_from_larger_applies({"a": 5.4, "b": 2.1, "op": "-"})

    def test_dropped_the_carry(self):
        # 0.9 + 0.8 -> 0.7 (correct is 1.7)
        p = {"a": 0.9, "b": 0.8, "op": "+"}
        assert M.dropped_the_carry(p) == "0.7"

    def test_dropped_the_carry_applies(self):
        assert M.dropped_the_carry_applies({"a": 0.9, "b": 0.8, "op": "+"})
        # 0.2 + 0.3 = 0.5 (no carry -> returns None -> applies False)
        assert not M.dropped_the_carry_applies({"a": 0.2, "b": 0.3, "op": "+"})

    def test_used_the_wrong_operation(self):
        # 3.5 + 1.25 -> |3.5 - 1.25| = 2.25
        assert M.used_the_wrong_operation(self.P_ADD) == "2.25"
        # 5.4 - 2.18 -> 5.4 + 2.18 = 7.58
        assert M.used_the_wrong_operation(self.P_SUB) == "7.58"

    def test_forgot_the_decimal_point(self):
        # 3.5 + 1.25 = 4.75 -> 475
        assert M.forgot_the_decimal_point(self.P_ADD) == "475"
        # 5.4 - 2.18 = 3.22 -> 322
        assert M.forgot_the_decimal_point(self.P_SUB) == "322"

# ---------- g5-multiply ----------
class TestMultiply:
    P = {"a": 23, "b": 14}  # 23 * 14 = 322

    def test_forgot_the_placeholder_zero(self):
        # 23*4 + 23*1 = 92 + 23 = 115
        assert M.forgot_the_placeholder_zero(self.P) == "115"

    def test_multiplied_only_the_ones_digit(self):
        # 23*4 = 92
        assert M.multiplied_only_the_ones_digit(self.P) == "92"

    def test_skipped_the_cross_products(self):
        # (20*10) + (3*4) = 200 + 12 = 212
        assert M.skipped_the_cross_products(self.P) == "212"

    def test_added_instead_of_multiplying(self):
        # 23 + 14 = 37
        assert M.added_instead_of_multiplying(self.P) == "37"

    def test_put_the_zero_on_the_wrong_row(self):
        # 23*4*10 + 23*1 = 920 + 23 = 943
        assert M.put_the_zero_on_the_wrong_row(self.P) == "943"

# ---------- g6-fraction-division ----------
class TestFractionDivision:
    P = {"a": 2, "b": 3, "c": 1, "d": 4}  # 2/3 / 1/4 = 8/3

    def test_multiplied_without_flipping(self):
        # (2*1)/(3*4) = 2/12 = 1/6
        assert M.multiplied_without_flipping(self.P) == "1/6"

    def test_flipped_the_first_fraction(self):
        # (3*1)/(2*4) = 3/8
        assert M.flipped_the_first_fraction(self.P) == "3/8"

    def test_flipped_both_fractions(self):
        # (3*4)/(2*1) = 12/2 = 6
        assert M.flipped_both_fractions(self.P) == "6"

    def test_added_instead_of_dividing(self):
        # 2/3 + 1/4 = 8/12 + 3/12 = 11/12
        assert M.added_instead_of_dividing(self.P) == "11/12"
