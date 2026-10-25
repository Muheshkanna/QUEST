import sys, os, pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import api._lib.misconceptions as M

# ---------- g5-fractions-add ----------
class TestFractionsAdd:
    P = {"a": 1, "b": 4, "c": 1, "d": 8}  # 1/4 + 1/8

    def test_added_tops_and_bottoms(self):
        # (1+1)/(4+8) = 2/12 = 1/6
        assert M.added_tops_and_bottoms(self.P) == "1/6"

    def test_renamed_bottom_kept_tops(self):
        # lcm(4,8)=8; (1+1)/8 = 2/8 = 1/4
        assert M.renamed_bottom_kept_tops(self.P) == "1/4"

    def test_renamed_bottom_kept_tops_applies_same_denom(self):
        assert not M.renamed_bottom_kept_tops_applies({"a":1,"b":4,"c":1,"d":4})

    def test_multiplied_instead_of_adding(self):
        # 1*1 / 4*8 = 1/32
        assert M.multiplied_instead_of_adding(self.P) == "1/32"

    def test_subtracted_instead_of_adding(self):
        # |1/4 - 1/8| = 1/8
        assert M.subtracted_instead_of_adding(self.P) == "1/8"

    def test_subtracted_instead_of_adding_applies_false_when_equal(self):
        # 1/4 + 1/4 -> diff=0 -> should not apply
        assert not M.subtracted_instead_of_adding_applies({"a":1,"b":4,"c":1,"d":4})

    def test_added_tops_kept_first_bottom(self):
        # (1+1)/4 = 2/4 = 1/2
        assert M.added_tops_kept_first_bottom(self.P) == "1/2"

    def test_added_tops_kept_first_bottom_applies_same_denom(self):
        assert not M.added_tops_kept_first_bottom_applies({"a":1,"b":8,"c":1,"d":8})

# ---------- g5-volume ----------
class TestVolume:
    P = {"l": 6, "w": 6, "h": 4}

    def test_added_the_sides(self):
        assert M.added_the_sides(self.P) == "16"

    def test_found_base_area_only(self):
        assert M.found_base_area_only(self.P) == "36"

    def test_used_surface_area_formula(self):
        # 2*(36+24+24) = 168
        assert M.used_surface_area_formula(self.P) == "168"

    def test_multiplied_two_sides_then_added_height(self):
        # 6*6 + 4 = 40
        assert M.multiplied_two_sides_then_added_height(self.P) == "40"

    def test_cubed_one_side(self):
        # 6^3 = 216
        assert M.cubed_one_side(self.P) == "216"

    def test_cubed_one_side_applies_false_when_equal(self):
        assert not M.cubed_one_side_applies({"l":4,"w":4,"h":4})

# ---------- g6-percents ----------
class TestPercents:
    P = {"p": 15, "n": 60}

    def test_multiplied_by_percent_number(self):
        assert M.multiplied_by_percent_number(self.P) == "900"

    def test_moved_decimal_wrong_way(self):
        # (15/10)*60 = 90
        assert M.moved_decimal_wrong_way(self.P) == "90"

    def test_found_the_leftover_amount(self):
        # 60 - 9 = 51
        assert M.found_the_leftover_amount(self.P) == "51"

    def test_divided_instead_of_multiplying(self):
        # 60/15 = 4
        assert M.divided_instead_of_multiplying(self.P) == "4"

    def test_found_one_percent_only(self):
        # 60/100 = 0.6
        assert M.found_one_percent_only(self.P) == "0.6"

# ---------- g6-equations ----------
class TestEquations:
    P_ax_b = {"form": "ax_b", "a": 6, "b": 54}
    P_xpa_b = {"form": "xpa_b", "a": 5, "b": 12}
    P_axpb_c = {"form": "axpb_c", "a": 2, "b": 3, "c": 11}

    def test_subtracted_instead_of_dividing(self):
        # 54 - 6 = 48
        assert M.subtracted_instead_of_dividing(self.P_ax_b) == "48"

    def test_subtracted_instead_of_dividing_applies_wrong_form(self):
        assert not M.subtracted_instead_of_dividing_applies(self.P_xpa_b)

    def test_multiplied_instead_of_dividing(self):
        # 6*54 = 324
        assert M.multiplied_instead_of_dividing(self.P_ax_b) == "324"

    def test_divided_the_wrong_way(self):
        # 6/54 = 1/9
        assert M.divided_the_wrong_way(self.P_ax_b) == "1/9"

    def test_ignored_the_coefficient(self):
        # just 54
        assert M.ignored_the_coefficient(self.P_ax_b) == "54"

    def test_added_instead_of_subtracting(self):
        # 5+12 = 17
        assert M.added_instead_of_subtracting(self.P_xpa_b) == "17"

    def test_added_instead_of_subtracting_applies_wrong_form(self):
        assert not M.added_instead_of_subtracting_applies(self.P_ax_b)

    def test_subtracted_the_wrong_way(self):
        # 5-12 = -7
        assert M.subtracted_the_wrong_way(self.P_xpa_b) == "-7"

    def test_undid_multiplication_first(self):
        # c/a - b = 11/2 - 3 = 5.5-3 = 2.5 -> as fraction: 5/2 - 3 = -1/2? Wait: Fraction(11,2)-3 = 5/2
        # 11/2 = 5.5; 5.5 - 3 = 2.5 = 5/2
        assert M.undid_multiplication_first(self.P_axpb_c) == "5/2"

    def test_added_the_constant(self):
        # (11+3)/2 = 7
        assert M.added_the_constant(self.P_axpb_c) == "7"

    def test_ignored_the_constant_term(self):
        # 11/2 = 11/2
        assert M.ignored_the_constant_term(self.P_axpb_c) == "11/2"

# ---------- g5-divide ----------
class TestDivide:
    P = {"n": 451, "d": 16, "q": 28, "r": 3}

    def test_dropped_the_remainder(self):
        assert M.dropped_the_remainder(self.P) == "28 R 0"

    def test_swapped_quotient_and_remainder(self):
        assert M.swapped_quotient_and_remainder(self.P) == "3 R 28"

    def test_stopped_subtracting_too_early(self):
        # (28-1) R (3+16) = 27 R 19
        assert M.stopped_subtracting_too_early(self.P) == "27 R 19"

    def test_stopped_subtracting_too_early_applies_q0(self):
        assert not M.stopped_subtracting_too_early_applies({"n":9,"d":9,"q":0,"r":9})

    def test_misplaced_quotient_digit(self):
        # 28*10 R 3 = 280 R 3
        assert M.misplaced_quotient_digit(self.P) == "280 R 3"

    def test_rounded_quotient_up_kept_remainder(self):
        # 29 R 3
        assert M.rounded_quotient_up_kept_remainder(self.P) == "29 R 3"
