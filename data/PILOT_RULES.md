=== PILOT RULES ===
General: every rule maps params -> wrong answer. Skip a distractor if it equals the correct answer, duplicates another option, or its applies_when is false. Never use the same rule twice in one question. A question needs 3 valid distractors, otherwise redraw params. Never pad with filler.

g5-fractions-add (params a/b + c/d)
- added_tops_and_bottoms: (a+c)/(b+d). Label "You added the tops and the bottoms." Example 1/4+1/8 -> 2/12
- renamed_bottom_kept_tops: only when b != d; L = lcm(b,d); (a+c)/L. Label "You found a common bottom but forgot to change the tops." 1/4+1/8 -> 2/8
- multiplied_instead_of_adding: (a*c)/(b*d). 1/4+1/8 -> 1/32
- subtracted_instead_of_adding: |a/b - c/d|, only if > 0. Label "You subtracted instead of adding." 1/4+1/8 -> 1/8
- added_tops_kept_first_bottom: only when b != d; (a+c)/b. 1/4+1/8 -> 2/4

g5-volume (params l, w, h)
- added_the_sides: l+w+h. 6,6,4 -> 16
- found_base_area_only: l*w. 6,6,4 -> 36
- used_surface_area_formula: 2*(l*w + l*h + w*h). 6,6,4 -> 168
- multiplied_two_sides_then_added_height: l*w + h. 6,6,4 -> 40
- cubed_one_side: l*l*l, only when l, w, h are not all equal. 6,6,4 -> 216

g6-percents (params p% of n)
- multiplied_by_percent_number: p*n. 15% of 60 -> 900
- moved_decimal_wrong_way: (p/10)*n. 15% of 60 -> 90
- found_the_leftover_amount: n - (p/100*n). 15% of 60 -> 51
- divided_instead_of_multiplying: n/p, only if different from the correct answer. 15% of 60 -> 4
- found_one_percent_only: n/100. 15% of 60 -> 0.6

g6-equations
 Form a*x = b (correct b/a):
- subtracted_instead_of_dividing: b - a. 6x=54 -> 48
- multiplied_instead_of_dividing: a*b. 6x=54 -> 324
- divided_the_wrong_way: a/b. 6x=54 -> 1/9
- ignored_the_coefficient: b. 6x=54 -> 54
 Form x + a = b (correct b-a):
- added_instead_of_subtracting: a + b
- subtracted_the_wrong_way: a - b (only if different from the correct answer)
 Form a*x + b = c (hard; correct (c-b)/a):
- undid_multiplication_first: c/a - b
- added_the_constant: (c + b)/a
- ignored_the_constant_term: c/a

g5-divide (params n / d = q R r; use only problems with r != 0)
- dropped_the_remainder: "q R 0". 451/16 -> 28 R 0
- swapped_quotient_and_remainder: "r R q". 451/16 -> 3 R 28
- stopped_subtracting_too_early: "(q-1) R (r+d)", only if q >= 1. 451/16 -> 27 R 19
- misplaced_quotient_digit: "(q*10) R r". 451/16 -> 280 R 3
- rounded_quotient_up_kept_remainder: "(q+1) R r". 451/16 -> 29 R 3
=== END PILOT RULES ===
