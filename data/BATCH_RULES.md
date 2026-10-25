# BATCH_RULES.md — Source of Truth for Quest Curriculum Rollout

Every rule maps `params -> wrong answer`. Skip a distractor if it equals the correct answer, duplicates another option, or its `applies_when` is false. Never use the same rule twice in one question. A question needs 3 valid distractors, otherwise redraw params. Never pad with filler.

---

## BATCH A (Topics 6–9)

### 1. g6-ratios (params: a, b, k where equivalent ratio is k*a : k*b)
- `additive_ratio_scaling`: `(a+k) : (b+k)`. Student adds the multiplier to both terms instead of multiplying.
  * Example: Ratio 2:3 scaled by 4 -> (2+4):(3+4) = 6:7 (correct: 8:12)
  * Kid label: "You added the scaling number to both sides instead of multiplying."
  * Applies when: `k > 1`
- `inverts_ratio_terms_order`: `(k*b) : (k*a)`. Student reverses antecedent and consequent.
  * Example: Ratio 2:3 scaled by 4 -> 12:8 (correct: 8:12)
  * Kid label: "You swapped the order of the ratio terms."
  * Applies when: `a != b`
- `multiplied_only_first_term`: `(k*a) : b`. Student multiplies the first quantity but forgets to scale the second.
  * Example: Ratio 2:3 scaled by 4 -> 8:3 (correct: 8:12)
  * Kid label: "You only multiplied the first number in the ratio."
  * Applies when: `k > 1`
- `part_to_part_vs_part_to_whole`: `(k*a) : (k*a + k*b)`. Student compares part to total instead of part to part.
  * Example: Ratio 2:3 scaled by 4 with total 20 -> 8:20 (correct: 8:12)
  * Kid label: "You compared a part to the whole total instead of part to part."
  * Applies when: `True`
- `squared_terms`: `(a*a) : (b*b)`. Student squares both numbers instead of multiplying by scale factor.
  * Example: Ratio 2:3 scaled by 4 -> 4:9 (correct: 8:12)
  * Kid label: "You multiplied each number by itself instead of the scaling factor."
  * Applies when: `k != a and k != b`

### 2. g6-unit-rates (params: a units, b measures, correct rate a/b)
- `divides_in_reversed_order`: `b/a`. Student divides total measure by quantity instead of quantity by measure.
  * Example: 180 miles in 3 hours -> 3/180 = 1/60 mph (correct: 60 mph)
  * Kid label: "You divided in reverse order."
  * Applies when: `a != b`
- `multiplies_instead_of_dividing`: `a * b`. Student multiplies the numbers instead of dividing to find rate per 1.
  * Example: 180 miles in 3 hours -> 180 * 3 = 540 mph (correct: 60 mph)
  * Kid label: "You multiplied the numbers instead of finding the rate for 1 unit."
  * Applies when: `b > 1`
- `forgets_unit_rate_denominator_is_one`: `a`. Student reports the total quantity without dividing by denominator.
  * Example: 180 miles in 3 hours -> 180 mph (correct: 60 mph)
  * Kid label: "You kept the total number instead of dividing to find the rate per 1."
  * Applies when: `b > 1`
- `subtracts_quantities`: `a - b`. Student subtracts instead of dividing.
  * Example: 180 miles in 3 hours -> 180 - 3 = 177 (correct: 60)
  * Kid label: "You subtracted the numbers instead of dividing to find the rate."
  * Applies when: `True`
- `adds_quantities`: `a + b`. Student adds instead of dividing.
  * Example: 180 miles in 3 hours -> 180 + 3 = 183 (correct: 60)
  * Kid label: "You added the numbers together instead of dividing."
  * Applies when: `True`

### 3. g5-fractions-multiply (params: a/b * c/d, correct (a*c)/(b*d))
- `added_fractions_instead`: `a/b + c/d`. Student adds the fractions instead of multiplying.
  * Example: 2/3 * 1/4 -> 8/12 + 3/12 = 11/12 (correct: 2/12 = 1/6)
  * Kid label: "You added the fractions instead of multiplying them."
  * Applies when: `True`
- `cross_multiplies_instead_of_multiplying_straight`: `(a*d)/(b*c)`. Student cross-multiplies numerators and denominators.
  * Example: 2/3 * 1/4 -> (2*4)/(3*1) = 8/3 (correct: 1/6)
  * Kid label: "You cross-multiplied instead of multiplying straight across."
  * Applies when: `(a*d != a*c) and (b*c != b*d)`
- `multiplies_tops_adds_bottoms`: `(a*c)/(b+d)`. Student multiplies tops but adds bottoms.
  * Example: 2/3 * 1/4 -> (2*1)/(3+4) = 2/7 (correct: 1/6)
  * Kid label: "You multiplied the top numbers but added the bottom numbers."
  * Applies when: `b + d != b * d`
- `added_tops_multiplied_bottoms`: `(a+c)/(b*d)`. Student adds tops but multiplies bottoms.
  * Example: 2/3 * 1/4 -> (2+1)/(3*4) = 3/12 = 1/4 (correct: 1/6)
  * Kid label: "You added the top numbers instead of multiplying them."
  * Applies when: `a + c != a * c`
- `multiplies_both_by_whole_number`: For whole w * a/b, student multiplies both top and bottom: `(w*a)/(w*b)`.
  * Example: 3 * (2/5) -> (3*2)/(3*5) = 6/15 = 2/5 (correct: 6/5)
  * Kid label: "You multiplied both the top and bottom by the whole number."
  * Applies when: `problem_has_whole_number`

### 4. g6-mean-median (params: list X = [x1, ..., xk])
- `finds_median_without_ordering_data`: Middle element of raw unsorted list.
  * Example: [9, 2, 7, 1, 5] -> raw middle is 7 (sorted [1, 2, 5, 7, 9], correct median is 5)
  * Kid label: "You picked the middle number without putting the list in order first."
  * Applies when: `raw_middle != sorted_middle`
- `confuses_mean_with_median`: Computes mean when asked for median, or median when asked for mean.
  * Example: [2, 4, 9] (mean is 5, median is 4) -> returns 5 when median requested
  * Kid label: "You calculated the mean (average) instead of finding the median (middle)."
  * Applies when: `mean != median`
- `divides_sum_by_arbitrary_number`: Sum divided by 2 instead of count k.
  * Example: [2, 4, 6, 8] sum = 20, count = 4 -> 20 / 2 = 10 (correct mean: 5)
  * Kid label: "You divided the total sum by 2 instead of how many numbers there are."
  * Applies when: `k != 2`
- `finds_range_instead`: `max(X) - min(X)`. Student calculates statistical range instead of center.
  * Example: [2, 5, 9] -> 9 - 2 = 7 (correct median: 5)
  * Kid label: "You found the range (highest minus lowest) instead of the middle value."
  * Applies when: `range_val != correct`
- `ignores_middle_average_for_even_count`: For even count, takes first middle value instead of average of two middles.
  * Example: [2, 4, 6, 8] -> returns 4 (correct median: 5)
  * Kid label: "For an even number of values, you must find the halfway point between the two middle numbers."
  * Applies when: `len(X) % 2 == 0 and middle1 != middle2`

---

## REMAINING 11 TOPICS (PROPOSED RULES)

### 5. g5-place-value (params: n, shift k, op in ['multiply', 'divide'])
- `additive_power_of_ten`: Adds 10*k to n instead of multiplying by 10^k. Example: 45 * 10^2 -> 45 + 20 = 65 (correct: 4500).
- `decimal_point_shift_reversed`: Shifts decimal point in wrong direction. Example: 4.5 * 10 -> 0.45 (correct: 45).
- `confuses_ten_times_with_add_ten`: Adds 10 instead of multiplying by 10. Example: 10 times 80 -> 90 (correct: 800).
- `drops_trailing_zeros`: Drops zeros instead of adding place value. Example: 50 * 100 -> 50 (correct: 5000).
- `counts_digits_not_zeros`: Multiplies by number of zeros instead of power of 10. Example: 15 * 100 -> 15 * 2 = 30.

### 6. g5-decimal-ops (params: a, b with decimals, op in ['+', '-'])
- `unaligned_decimals`: Aligns numbers to right like integers without aligning decimal points. Example: 3.5 + 1.25 -> aligns 5 with 5 giving 4.75 or 1.60.
- `ignores_empty_place_value`: Subtracts smaller digit from empty space without regrouping. Example: 5.4 - 2.18 -> 3.38 (correct: 3.22).
- `carries_over_decimal_point_incorrectly`: Resets carrying at the decimal point. Example: 0.9 + 0.8 -> 0.17 (correct: 1.7).
- `adds_instead_of_subtracting`: Performs addition when problem asks for subtraction.
- `subtracts_smaller_from_larger_regardless_of_order`: Inverts top and bottom in columns where bottom digit is larger.

### 7. g5-decimal-compare-round (params: decimals to compare or round)
- `longer_decimal_is_larger`: Assumes 0.125 > 0.5 because 125 > 5.
- `round_down_without_truncation_rule`: Truncates digits without checking if next digit >= 5. Example: round 3.47 to tenths -> 3.4 (correct: 3.5).
- `confuses_tenths_and_hundredths`: Compares hundredths digit directly to tenths digit.
- `rounds_wrong_place_value`: Rounds to whole number instead of tenths, or tenths instead of hundredths.
- `reverses_comparison_sign`: Writes < instead of > or vice-versa.

### 8. g5-fractions-divide-unit (params: 1/b / w or w / (1/b))
- `confuses_division_order`: Calculates w / (1/b) when problem asks for (1/b) / w. Example: (1/3) / 4 -> 12 (correct: 1/12).
- `multiplies_instead_of_dividing`: Multiplies whole by fraction. Example: 4 / (1/3) -> 4/3 (correct: 12).
- `fractional_quotient_confused_with_remainder`: Treats remainder as unit fraction.
- `keeps_same_fraction`: Returns 1/b without dividing.
- `inverts_wrong_number`: Inverts the dividend instead of divisor.

### 9. g5-multiply (params: 2-digit by 2-digit a * b)
- `forgets_tens_place_zero`: Forgets placeholder 0 in second partial product row.
- `multiplies_columns_only`: Multiplies tens*tens and ones*ones, omitting cross terms (e.g. 12 * 13 -> 106).
- `adds_carried_digit_before_multiplying`: Adds carried number before multiplying instead of after.
- `adds_numbers_instead_of_multiplying`: a + b.
- `aligns_partial_products_incorrectly`: Shifts partial products in wrong direction.

### 10. g5-order-ops (params: expression with +, -, *, /, parentheses)
- `computes_strictly_left_to_right`: Ignores multiplication/division precedence and calculates left to right. Example: 3 + 4 * 2 -> 14 (correct: 11).
- `ignores_parentheses`: Performs multiplication before parentheses. Example: 2 * (3 + 4) -> 6 + 4 = 10 (correct: 14).
- `performs_addition_before_subtraction`: Thinks PEMDAS means A always precedes S even left to right. Example: 10 - 3 + 2 -> 10 - 5 = 5 (correct: 9).
- `performs_multiplication_before_division`: Thinks M always precedes D left to right. Example: 12 / 3 * 2 -> 12 / 6 = 2 (correct: 8).
- `multiplies_terms_outside_brackets_first`: Multiplies outside before resolving inside brackets.

### 11. g6-fraction-division (params: a/b / c/d, correct (a*d)/(b*c))
- `multiplies_without_inverting`: (a*c)/(b*d). Multiplies straight across without inverting divisor. Example: 2/3 / 1/4 -> 2/12 = 1/6 (correct: 8/3).
- `inverts_first_fraction`: (b*c)/(a*d). Inverts dividend instead of divisor. Example: 2/3 / 1/4 -> 3/2 * 1/4 = 3/8 (correct: 8/3).
- `inverts_both_fractions`: (b*d)/(a*c). Inverts both fractions. Example: 2/3 / 1/4 -> 3/2 * 4/1 = 12/2 = 6 (correct: 8/3).
- `cross_adds`: Cross-adds numerators and denominators.
- `divides_tops_and_bottoms_directly`: (a/c)/(b/d) when not cleanly divisible.

### 12. g6-decimals (params: multi-digit decimal * or /)
- `misplaces_product_decimal_places`: Adds decimal places incorrectly (e.g. 0.2 * 0.3 -> 0.6 instead of 0.06).
- `ignores_divisor_decimal_shift`: Divides without shifting divisor decimal to whole number. Example: 12 / 0.3 -> 4 (correct: 40).
- `adds_decimals_instead_of_multiplying`: a + b instead of a * b.
- `counts_decimal_places_from_left`: Counts places from left of number instead of right.
- `drops_zero_after_decimal_point`: Treats 0.04 as 0.4.

### 13. g6-integers (params: a, b with signs or absolute values)
- `confuses_negative_magnitude`: Thinks -10 > -2 because 10 > 2.
- `absolute_value_makes_opposite`: Thinks |-5| = -5 or |5| = -5.
- `subtracts_negative_as_subtraction`: Treats a - (-b) as a - b instead of a + b.
- `adds_signs_arbitrarily`: In -4 + 6, writes -10 or -2.
- `confuses_opposite_with_reciprocal`: Thinks opposite of 4 is 1/4 instead of -4.

### 14. g6-equiv-expressions (params: a*(b*x + c) or combining like terms)
- `incomplete_distribution`: Multiplies coefficient by first term only: a*b*x + c. Example: 3*(2x + 4) -> 6x + 4 (correct: 6x + 12).
- `combines_unlike_terms`: Adds variable term and constant term together: (a*b + c)*x. Example: 6x + 4 -> 10x.
- `sign_error_distributing_negative`: Forgets that distributing a negative sign flips the sign of all inner terms.
- `distributes_to_outside_terms`: Multiplies terms not inside the parentheses.
- `squares_variable_on_distribution`: Thinks 2*(3x) = 6x^2 instead of 6x.

### 15. g6-exponents (params: a^b)
- `multiplies_base_by_exponent`: a * b instead of a^b. Example: 3^4 -> 12 (correct: 81).
- `adds_base_and_exponent`: a + b. Example: 3^4 -> 7 (correct: 81).
- `inverts_base_and_exponent`: b^a instead of a^b. Example: 2^3 -> 3^2 = 9 (correct: 8).
- `multiplies_exponent_by_itself`: b * b instead of a^b. Example: 3^4 -> 4 * 4 = 16.
- `treats_exponent_as_place_value`: Appends b zeros to a. Example: 2^3 -> 2000.
