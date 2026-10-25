import sys, os, pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import api._lib.misconceptions as M

# ---------- g6-ratios ----------
class TestRatios:
    P = {"a": 2, "b": 3, "k": 4}  # ratio 2:3 scaled by 4, correct = 8:12

    def test_additive_ratio_scaling(self):
        # (2+4):(3+4) = 6:7
        assert M.additive_ratio_scaling(self.P) == "6:7"

    def test_additive_ratio_scaling_applies(self):
        assert M.additive_ratio_scaling_applies(self.P)
        assert not M.additive_ratio_scaling_applies({"a": 2, "b": 3, "k": 1})

    def test_inverts_ratio_terms_order(self):
        # 4*3 : 4*2 = 12:8
        assert M.inverts_ratio_terms_order(self.P) == "12:8"

    def test_inverts_ratio_terms_order_applies(self):
        assert M.inverts_ratio_terms_order_applies(self.P)
        assert not M.inverts_ratio_terms_order_applies({"a": 3, "b": 3, "k": 2})

    def test_multiplied_only_first_term(self):
        # 4*2 : 3 = 8:3
        assert M.multiplied_only_first_term(self.P) == "8:3"

    def test_multiplied_only_first_term_applies(self):
        assert M.multiplied_only_first_term_applies(self.P)
        assert not M.multiplied_only_first_term_applies({"a": 2, "b": 3, "k": 1})

    def test_part_to_part_vs_part_to_whole(self):
        # 8 : (8 + 12) = 8:20
        assert M.part_to_part_vs_part_to_whole(self.P) == "8:20"

    def test_squared_terms(self):
        # 2*2 : 3*3 = 4:9
        assert M.squared_terms(self.P) == "4:9"

    def test_squared_terms_applies(self):
        assert M.squared_terms_applies(self.P)
        assert not M.squared_terms_applies({"a": 4, "b": 3, "k": 4})  # k == a

# ---------- g6-unit-rates ----------
class TestUnitRates:
    P = {"a": 180, "b": 3}  # 180 miles / 3 hours = 60 mph

    def test_divides_in_reversed_order(self):
        # 3/180 = 1/60
        assert M.divides_in_reversed_order(self.P) == "1/60"

    def test_divides_in_reversed_order_applies(self):
        assert M.divides_in_reversed_order_applies(self.P)
        assert not M.divides_in_reversed_order_applies({"a": 5, "b": 5})

    def test_forgets_unit_rate_denominator_is_one(self):
        # Student returns 180 (the total)
        assert M.forgets_unit_rate_denominator_is_one(self.P) == "180"

    def test_forgets_unit_rate_denominator_is_one_applies(self):
        assert M.forgets_unit_rate_denominator_is_one_applies(self.P)
        assert not M.forgets_unit_rate_denominator_is_one_applies({"a": 5, "b": 1})

    def test_subtracts_quantities(self):
        # 180 - 3 = 177
        assert M.subtracts_quantities(self.P) == "177"

    def test_adds_quantities(self):
        # 180 + 3 = 183
        assert M.adds_quantities(self.P) == "183"

# ---------- g5-fractions-multiply ----------
class TestFractionsMultiply:
    # 2/3 * 1/4 = 2/12 = 1/6
    P = {"a": 2, "b": 3, "c": 1, "d": 4}

    def test_added_fractions_instead(self):
        # 2/3 + 1/4 = 8/12 + 3/12 = 11/12
        assert M.added_fractions_instead(self.P) == "11/12"

    def test_cross_multiplies_instead_of_multiplying_straight(self):
        # (2*4)/(3*1) = 8/3
        assert M.cross_multiplies_instead_of_multiplying_straight(self.P) == "8/3"

    def test_multiplies_tops_adds_bottoms(self):
        # (2*1)/(3+4) = 2/7
        assert M.multiplies_tops_adds_bottoms(self.P) == "2/7"

    def test_multiplies_tops_adds_bottoms_applies(self):
        assert M.multiplies_tops_adds_bottoms_applies(self.P)

    def test_added_tops_multiplied_bottoms(self):
        # (2+1)/(3*4) = 3/12 = 1/4
        assert M.added_tops_multiplied_bottoms(self.P) == "1/4"

    def test_added_tops_multiplied_bottoms_applies(self):
        assert M.added_tops_multiplied_bottoms_applies(self.P)

    def test_multiplies_both_by_whole_number(self):
        # whole number case: 3 * (2/5) -> (3*2)/(3*5) = 6/15 = 2/5
        pw = {"a": 2, "b": 5, "w": 3, "c": 3, "d": 1}
        assert M.multiplies_both_by_whole_number(pw) == "2/5"

    def test_multiplies_both_by_whole_number_applies(self):
        assert M.multiplies_both_by_whole_number_applies({"a": 2, "b": 5, "w": 3, "c": 3, "d": 1})
        assert not M.multiplies_both_by_whole_number_applies({"a": 2, "b": 3, "c": 1, "d": 4})

# ---------- g6-mean-median ----------
class TestMeanMedian:
    def test_finds_median_without_ordering_data(self):
        # [9, 2, 7, 1, 5] -> raw middle is 7
        p = {"data": [9, 2, 7, 1, 5], "target": "median"}
        assert M.finds_median_without_ordering_data(p) == "7"

    def test_finds_median_without_ordering_data_applies(self):
        p = {"data": [9, 2, 7, 1, 5], "target": "median"}
        assert M.finds_median_without_ordering_data_applies(p)
        # sorted: [1,2,5,7,9], median=5, raw middle=7 -> applies

    def test_confuses_mean_with_median(self):
        # [2, 4, 9] -> mean=5, median=4 -> when target=median, returns mean=5
        p = {"data": [2, 4, 9], "target": "median"}
        assert M.confuses_mean_with_median(p) == "5"

    def test_confuses_mean_with_median_applies(self):
        p = {"data": [2, 4, 9], "target": "median"}
        assert M.confuses_mean_with_median_applies(p)

    def test_gave_the_total_instead_of_the_mean(self):
        # [21, 5, 24, 15, 20] -> sum = 85 (correct mean = 17)
        p = {"data": [21, 5, 24, 15, 20], "target": "mean"}
        assert M.gave_the_total_instead_of_the_mean(p) == "85"

    def test_gave_the_total_instead_of_the_mean_applies(self):
        p = {"data": [21, 5, 24, 15, 20], "target": "mean"}
        assert M.gave_the_total_instead_of_the_mean_applies(p)

    def test_finds_range_instead(self):
        # [2, 5, 9] -> 9 - 2 = 7
        p = {"data": [2, 5, 9], "target": "median"}
        assert M.finds_range_instead(p) == "7"

    def test_finds_range_instead_applies(self):
        p = {"data": [2, 5, 9], "target": "median"}
        assert M.finds_range_instead_applies(p)

    def test_ignores_middle_average_for_even_count(self):
        # [2, 4, 6, 8] -> sorted [2,4,6,8], picks 4 instead of (4+6)/2=5
        p = {"data": [2, 4, 6, 8], "target": "median"}
        assert M.ignores_middle_average_for_even_count(p) == "4"

    def test_ignores_middle_average_for_even_count_applies(self):
        p = {"data": [2, 4, 6, 8], "target": "median"}
        assert M.ignores_middle_average_for_even_count_applies(p)
        # same middle values -> not applies
        p2 = {"data": [2, 5, 5, 8], "target": "median"}
        assert not M.ignores_middle_average_for_even_count_applies(p2)
