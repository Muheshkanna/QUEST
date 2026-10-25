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
- `multiplied_instead_of_dividing`: `a * b`. Student multiplies the numbers instead of dividing to find rate per 1.
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

### 3. g5-fractions-multiply (params: a/b * c/d, a/b != c/d, correct (a*c)/(b*d))
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

### 4. g6-mean-median (params: list X = [x1, ..., xk])
- `finds_median_without_ordering_data`: Middle element of raw unsorted list.
  * Example: [9, 2, 7, 1, 5] -> raw middle is 7 (sorted [1, 2, 5, 7, 9], correct median is 5)
  * Kid label: "You picked the middle number without putting the list in order first."
  * Applies when: `raw_middle != sorted_middle`
- `confuses_mean_with_median`: Computes mean when asked for median, or median when asked for mean.
  * Example: [2, 4, 9] (mean is 5, median is 4) -> returns 5 when median requested
  * Kid label: "You calculated the mean (average) instead of finding the median (middle)."
  * Applies when: `mean != median`
- `gave_the_total_instead_of_the_mean`: Sum of all numbers without dividing by count k.
  * Example: [21, 5, 24, 15, 20] -> returns sum = 85 (correct mean: 17)
  * Kid label: "You added all the numbers up but forgot to divide by how many there are."
  * Applies when: `True`
- `finds_range_instead`: `max(X) - min(X)`. Student calculates statistical range instead of center.
  * Example: [2, 5, 9] -> 9 - 2 = 7 (correct median: 5)
  * Kid label: "You found the range (highest minus lowest) instead of the middle value."
  * Applies when: `range_val != correct`
- `ignores_middle_average_for_even_count`: For even count, takes first middle value instead of average of two middles.
  * Example: [2, 4, 6, 8] -> returns 4 (correct median: 5)
  * Kid label: "For an even number of values, you must find the halfway point between the two middle numbers."
  * Applies when: `len(X) % 2 == 0 and middle1 != middle2`

---

## BATCH B RULES

(every rule: params -> wrong answer; skip a distractor if it equals the correct answer, duplicates another option, or applies_when is false; never reuse a rule in one question; need 3 genuine distractors else redraw params; no filler)

### 5. g5-decimal-ops (params a, b with different numbers of decimal places, op + or -)
- `ignored_the_decimal_point`: strip points, add/subtract as integers, place the point with max(places of a, b) digits. 3.5 + 1.25: 35 + 125 = 160 -> 1.60 = 1.6 (correct 4.75). Applies only if the integer subtraction is not negative.
- `subtracted_smaller_digit_from_larger`: subtraction only; pad to equal places, take |difference| per column. 5.4 - 2.18: 5.40 - 2.18 -> 3.38 (correct 3.22). Applies only if some column needs regrouping.
- `dropped_the_carry`: addition only; add digit by digit, keep the ones digit, discard carries. 0.9 + 0.8 -> 0.7 (correct 1.7). Skip if equal to the correct answer.
- `used_the_wrong_operation`: for addition |a - b|; for subtraction a + b. 3.5 + 1.25 -> 2.25.
- `forgot_the_decimal_point`: the right digits with no point. 3.5 + 1.25 -> 475.
Difficulty: easy = same number of places, no regrouping; medium = different places; hard = regrouping across the decimal point plus a two-step word problem.

### 6. g5-multiply (params a, b two-digit; neither ends in 0; b >= 12)
- `forgot_the_placeholder_zero`: a*(b mod 10) + a*(b div 10). 23 x 14: 92 + 23 = 115 (correct 322).
- `multiplied_only_the_ones_digit`: a*(b mod 10). 23 x 14 -> 92.
- `skipped_the_cross_products`: (10*(a div 10))*(10*(b div 10)) + (a mod 10)*(b mod 10). 23 x 14: 200 + 12 = 212.
- `added_instead_of_multiplying`: a + b. 23 + 14 = 37.
- `put_the_zero_on_the_wrong_row`: a*(b mod 10)*10 + a*(b div 10). 23 x 14: 920 + 23 = 943.
Difficulty: easy = 2-digit x 1-digit-tens (for example 23 x 12 with small digits), medium = typical 2-digit x 2-digit, hard = 3-digit x 2-digit word problem (keep the rules valid using a div 10 style terms for the hundreds digit, or restrict hard to 2-digit x 2-digit with larger digits).

### 7. g6-fraction-division (params a/b / c/d, a/b != c/d; correct (a*d)/(b*c))
- `multiplied_without_flipping`: (a*c)/(b*d). 2/3 / 1/4 -> 2/12 = 1/6 (correct 8/3).
- `flipped_the_first_fraction`: (b*c)/(a*d). -> 3/8.
- `flipped_both_fractions`: (b*d)/(a*c). -> 12/2 = 6.
- `added_instead_of_dividing`: a/b + c/d. -> 11/12.
Easy = divide by a unit fraction, medium = both fractions proper, hard = word problem with a mixed or whole number.

---

## REMAINING TOPICS
g5-place-value, g5-decimal-compare-round, g5-fractions-divide-unit, g5-order-ops, g6-decimals, g6-integers, g6-equiv-expressions, g6-exponents are NOT generated. Leave their banks empty so the safety valve marks them "Coming soon", and list them in the README as incomplete.
