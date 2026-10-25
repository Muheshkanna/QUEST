from fractions import Fraction
from math import lcm
from typing import Dict, Optional, Callable, Tuple
import json, os

_registry_cache = None

def load_registry():
    global _registry_cache
    if _registry_cache is None:
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'misconceptions.json'))
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        _registry_cache = {e['id']: e for e in data.get('misconceptions', [])}
    return _registry_cache

def reset_registry_cache():
    global _registry_cache
    _registry_cache = None

def _fmt_frac(f: Fraction) -> str:
    if f.denominator == 1:
        return str(f.numerator)
    return f'{f.numerator}/{f.denominator}'

def _fmt_num(v) -> str:
    if isinstance(v, float):
        if v == int(v):
            return str(int(v))
        return f'{v:.4f}'.rstrip('0').rstrip('.')
    return str(int(v)) if isinstance(v, (int, float)) and float(v) == int(float(v)) else str(v)

# ---- g5-fractions-add ----
def added_tops_and_bottoms(p):
    return _fmt_frac(Fraction(p['a'] + p['c'], p['b'] + p['d']))
def added_tops_and_bottoms_applies(p): return True

def renamed_bottom_kept_tops(p):
    return _fmt_frac(Fraction(p['a'] + p['c'], lcm(p['b'], p['d'])))
def renamed_bottom_kept_tops_applies(p): return p['b'] != p['d']

def multiplied_instead_of_adding(p):
    return _fmt_frac(Fraction(p['a'] * p['c'], p['b'] * p['d']))
def multiplied_instead_of_adding_applies(p): return True

def subtracted_instead_of_adding(p):
    return _fmt_frac(abs(Fraction(p['a'], p['b']) - Fraction(p['c'], p['d'])))
def subtracted_instead_of_adding_applies(p):
    return abs(Fraction(p['a'], p['b']) - Fraction(p['c'], p['d'])) > 0

def added_tops_kept_first_bottom(p):
    return _fmt_frac(Fraction(p['a'] + p['c'], p['b']))
def added_tops_kept_first_bottom_applies(p): return p['b'] != p['d']

# ---- g5-volume ----
def added_the_sides(p): return _fmt_num(p['l'] + p['w'] + p['h'])
def added_the_sides_applies(p): return True

def found_base_area_only(p): return _fmt_num(p['l'] * p['w'])
def found_base_area_only_applies(p): return True

def used_surface_area_formula(p):
    l, w, h = p['l'], p['w'], p['h']
    return _fmt_num(2 * (l*w + l*h + w*h))
def used_surface_area_formula_applies(p): return True

def multiplied_two_sides_then_added_height(p):
    return _fmt_num(p['l'] * p['w'] + p['h'])
def multiplied_two_sides_then_added_height_applies(p): return True

def cubed_one_side(p): return _fmt_num(p['l'] ** 3)
def cubed_one_side_applies(p): return not (p['l'] == p['w'] == p['h'])

# ---- g6-percents ----
def multiplied_by_percent_number(p): return _fmt_num(p['p'] * p['n'])
def multiplied_by_percent_number_applies(p): return True

def moved_decimal_wrong_way(p): return _fmt_num((p['p'] / 10) * p['n'])
def moved_decimal_wrong_way_applies(p): return True

def found_the_leftover_amount(p):
    return _fmt_num(p['n'] - (p['p'] / 100) * p['n'])
def found_the_leftover_amount_applies(p): return True

def divided_instead_of_multiplying(p):
    return _fmt_num(p['n'] / p['p'])
def divided_instead_of_multiplying_applies(p):
    return abs(p['n'] / p['p'] - (p['p'] / 100) * p['n']) > 1e-9

def found_one_percent_only(p): return _fmt_num(p['n'] / 100)
def found_one_percent_only_applies(p): return True

# ---- g6-equations ----
def subtracted_instead_of_dividing(p): return _fmt_num(p['b'] - p['a'])
def subtracted_instead_of_dividing_applies(p): return p.get('form') == 'ax_b'

def multiplied_instead_of_dividing(p): return _fmt_num(p['a'] * p['b'])
def multiplies_instead_of_dividing_applies(p):
    if 'form' in p:
        return p.get('form') == 'ax_b'
    return p.get('b', 1) > 1

def divided_the_wrong_way(p): return _fmt_frac(Fraction(p['a'], p['b']))
def divided_the_wrong_way_applies(p): return p.get('form') == 'ax_b'

def ignored_the_coefficient(p): return _fmt_num(p['b'])
def ignored_the_coefficient_applies(p): return p.get('form') == 'ax_b'

def added_instead_of_subtracting(p): return _fmt_num(p['a'] + p['b'])
def added_instead_of_subtracting_applies(p): return p.get('form') == 'xpa_b'

def subtracted_the_wrong_way(p): return _fmt_num(p['a'] - p['b'])
def subtracted_the_wrong_way_applies(p):
    return p.get('form') == 'xpa_b' and (p['a'] - p['b']) != (p['b'] - p['a'])

def ignored_the_added_value(p): return _fmt_num(p['b'])
def ignored_the_added_value_applies(p):
    correct = p['b'] - p['a']
    return p.get('form') == 'xpa_b' and p['b'] != correct

def used_added_value_as_answer(p): return _fmt_num(p['a'])
def used_added_value_as_answer_applies(p):
    correct = p['b'] - p['a']
    return p.get('form') == 'xpa_b' and p['a'] != correct

def undid_multiplication_first(p):
    return _fmt_frac(Fraction(p['c'], p['a']) - p['b'])
def undid_multiplication_first_applies(p): return p.get('form') == 'axpb_c'

def added_the_constant(p):
    return _fmt_frac(Fraction(p['c'] + p['b'], p['a']))
def added_the_constant_applies(p): return p.get('form') == 'axpb_c'

def ignored_the_constant_term(p):
    return _fmt_frac(Fraction(p['c'], p['a']))
def ignored_the_constant_term_applies(p): return p.get('form') == 'axpb_c'

# ---- g5-divide ----
def dropped_the_remainder(p): return f"{p['q']} R 0"
def dropped_the_remainder_applies(p): return True

def swapped_quotient_and_remainder(p): return f"{p['r']} R {p['q']}"
def swapped_quotient_and_remainder_applies(p): return True

def stopped_subtracting_too_early(p):
    return f"{p['q']-1} R {p['r']+p['d']}"
def stopped_subtracting_too_early_applies(p): return p['q'] >= 1

def misplaced_quotient_digit(p): return f"{p['q']*10} R {p['r']}"
def misplaced_quotient_digit_applies(p): return True

def rounded_quotient_up_kept_remainder(p): return f"{p['q']+1} R {p['r']}"
def rounded_quotient_up_kept_remainder_applies(p): return True

# ---- BATCH A: g6-ratios ----
def additive_ratio_scaling(p):
    k = p.get('k', 1)
    return f"{p['a'] + k}:{p['b'] + k}"
def additive_ratio_scaling_applies(p): return p.get('k', 1) > 1

def inverts_ratio_terms_order(p):
    k = p.get('k', 1)
    return f"{k * p['b']}:{k * p['a']}"
def inverts_ratio_terms_order_applies(p): return p['a'] != p['b']

def multiplied_only_first_term(p):
    k = p.get('k', 1)
    return f"{k * p['a']}:{p['b']}"
def multiplied_only_first_term_applies(p): return p.get('k', 1) > 1

def part_to_part_vs_part_to_whole(p):
    k = p.get('k', 1)
    return f"{k * p['a']}:{k * p['a'] + k * p['b']}"
def part_to_part_vs_part_to_whole_applies(p): return True

def squared_terms(p):
    return f"{p['a'] * p['a']}:{p['b'] * p['b']}"
def squared_terms_applies(p):
    k = p.get('k', 1)
    return k != p['a'] and k != p['b']

# ---- BATCH A: g6-unit-rates ----
def divides_in_reversed_order(p):
    return _fmt_frac(Fraction(p['b'], p['a']))
def divides_in_reversed_order_applies(p): return p['a'] != p['b']

def forgets_unit_rate_denominator_is_one(p):
    return _fmt_num(p['a'])
def forgets_unit_rate_denominator_is_one_applies(p): return p.get('b', 1) > 1

def subtracts_quantities(p):
    return _fmt_num(p['a'] - p['b'])
def subtracts_quantities_applies(p): return True

def adds_quantities(p):
    return _fmt_num(p['a'] + p['b'])
def adds_quantities_applies(p): return True

# ---- BATCH A: g5-fractions-multiply ----
def added_fractions_instead(p):
    c = p.get('c', p.get('w', 1))
    d = p.get('d', 1)
    return _fmt_frac(Fraction(p['a'], p['b']) + Fraction(c, d))
def added_fractions_instead_applies(p): return True

def cross_multiplies_instead_of_multiplying_straight(p):
    c = p.get('c', p.get('w', 1))
    d = p.get('d', 1)
    return _fmt_frac(Fraction(p['a'] * d, p['b'] * c))
def cross_multiplies_instead_of_multiplying_straight_applies(p):
    c = p.get('c', p.get('w', 1))
    d = p.get('d', 1)
    return (p['a'] * d != p['a'] * c) or (p['b'] * c != p['b'] * d)

def multiplies_tops_adds_bottoms(p):
    c = p.get('c', p.get('w', 1))
    d = p.get('d', 1)
    return _fmt_frac(Fraction(p['a'] * c, p['b'] + d))
def multiplies_tops_adds_bottoms_applies(p):
    d = p.get('d', 1)
    return p['b'] + d != p['b'] * d

def added_tops_multiplied_bottoms(p):
    c = p.get('c', p.get('w', 1))
    d = p.get('d', 1)
    return _fmt_frac(Fraction(p['a'] + c, p['b'] * d))
def added_tops_multiplied_bottoms_applies(p):
    c = p.get('c', p.get('w', 1))
    return p['a'] + c != p['a'] * c

def multiplies_both_by_whole_number(p):
    if 'w' in p:
        w = p['w']
        return _fmt_frac(Fraction(w * p['a'], w * p['b']))
    elif p.get('d') == 1:
        w = p['c']
        return _fmt_frac(Fraction(w * p['a'], w * p['b']))
    elif p.get('b') == 1:
        w = p['a']
        return _fmt_frac(Fraction(w * p['c'], w * p['d']))
    return _fmt_frac(Fraction(p['a'], p['b']))
def multiplies_both_by_whole_number_applies(p):
    return p.get('w') is not None or p.get('d') == 1 or p.get('b') == 1

# ---- BATCH A: g6-mean-median ----
def finds_median_without_ordering_data(p):
    data = p['data']
    n = len(data)
    return _fmt_num(data[n // 2])
def finds_median_without_ordering_data_applies(p):
    s = sorted(p['data'])
    n = len(s)
    corr = s[n // 2] if n % 2 == 1 else (s[n // 2 - 1] + s[n // 2]) / 2
    raw = p['data'][len(p['data']) // 2]
    return raw != corr

def confuses_mean_with_median(p):
    data = p['data']
    s = sorted(data)
    n = len(s)
    med = s[n // 2] if n % 2 == 1 else (s[n // 2 - 1] + s[n // 2]) / 2
    mean_val = sum(data) / n
    target = p.get('target', 'median')
    if target == 'median':
        return _fmt_num(mean_val)
    else:
        return _fmt_num(med)
def confuses_mean_with_median_applies(p):
    s = sorted(p['data'])
    n = len(s)
    med = s[n // 2] if n % 2 == 1 else (s[n // 2 - 1] + s[n // 2]) / 2
    mean_val = sum(p['data']) / n
    return med != mean_val

def gave_the_total_instead_of_the_mean(p):
    return _fmt_num(sum(p['data']))
def gave_the_total_instead_of_the_mean_applies(p):
    return True

def finds_range_instead(p):
    return _fmt_num(max(p['data']) - min(p['data']))
def finds_range_instead_applies(p):
    s = sorted(p['data'])
    n = len(s)
    corr = (sum(p['data']) / n) if p.get('target') == 'mean' else (s[n // 2] if n % 2 == 1 else (s[n // 2 - 1] + s[n // 2]) / 2)
    return (max(p['data']) - min(p['data'])) != corr

def ignores_middle_average_for_even_count(p):
    s = sorted(p['data'])
    n = len(s)
    return _fmt_num(s[n // 2 - 1])
def ignores_middle_average_for_even_count_applies(p):
    s = sorted(p['data'])
    n = len(s)
    return n % 2 == 0 and s[n // 2 - 1] != s[n // 2]

# ---- BATCH B: g5-decimal-ops ----
def _count_dec_places(x):
    s = str(x)
    return len(s.split(".")[1]) if "." in s else 0

def ignored_the_decimal_point(p):
    sa = str(p['a']).replace(".", "")
    sb = str(p['b']).replace(".", "")
    ia, ib = int(sa), int(sb)
    max_places = max(_count_dec_places(p['a']), _count_dec_places(p['b']))
    val = ia + ib if p.get('op', '+') == '+' else ia - ib
    if val < 0:
        return None
    s_val = str(val).zfill(max_places + 1)
    res_str = s_val[:-max_places] + "." + s_val[-max_places:]
    return _fmt_num(float(res_str))

def ignored_the_decimal_point_applies(p):
    if p.get('op') == '-':
        sa = str(p['a']).replace(".", "")
        sb = str(p['b']).replace(".", "")
        return int(sa) - int(sb) >= 0
    return True

def subtracted_smaller_digit_from_larger(p):
    if p.get('op', '+') != '-':
        return None
    max_places = max(_count_dec_places(p['a']), _count_dec_places(p['b']))
    fmt = f"{{:.{max_places}f}}"
    sa = fmt.format(p['a'])
    sb = fmt.format(p['b'])
    res_chars = []
    for ca, cb in zip(sa, sb):
        if ca == '.':
            res_chars.append('.')
        else:
            res_chars.append(str(abs(int(ca) - int(cb))))
    return _fmt_num(float("".join(res_chars)))

def subtracted_smaller_digit_from_larger_applies(p):
    if p.get('op') != '-':
        return False
    max_places = max(_count_dec_places(p['a']), _count_dec_places(p['b']))
    fmt = f"{{:.{max_places}f}}"
    sa = fmt.format(p['a'])
    sb = fmt.format(p['b'])
    for ca, cb in zip(sa, sb):
        if ca != '.' and int(ca) < int(cb):
            return True
    return False

def dropped_the_carry(p):
    if p.get('op', '+') != '+':
        return None
    max_places = max(_count_dec_places(p['a']), _count_dec_places(p['b']))
    fmt = f"{{:.{max_places}f}}"
    sa = fmt.format(p['a'])
    sb = fmt.format(p['b'])
    ia_str, fa_str = sa.split('.')
    ib_str, fb_str = sb.split('.')
    max_int_len = max(len(ia_str), len(ib_str))
    ia_str = ia_str.zfill(max_int_len)
    ib_str = ib_str.zfill(max_int_len)
    res_digits = []
    for ca, cb in zip(ia_str, ib_str):
        res_digits.append(str((int(ca) + int(cb)) % 10))
    res_digits.append('.')
    for ca, cb in zip(fa_str, fb_str):
        res_digits.append(str((int(ca) + int(cb)) % 10))
    val = float("".join(res_digits))
    correct = round(p['a'] + p['b'], max_places)
    if round(val, max_places) == correct:
        return None
    return _fmt_num(val)

def dropped_the_carry_applies(p):
    if p.get('op') != '+':
        return False
    return dropped_the_carry(p) is not None

def used_the_wrong_operation(p):
    if p.get('op', '+') == '+':
        val = abs(p['a'] - p['b'])
    else:
        val = p['a'] + p['b']
    return _fmt_num(round(val, 6))

def used_the_wrong_operation_applies(p):
    return True

def forgot_the_decimal_point(p):
    max_places = max(_count_dec_places(p['a']), _count_dec_places(p['b']))
    if p.get('op', '+') == '+':
        val = round(p['a'] + p['b'], max_places)
    else:
        val = round(p['a'] - p['b'], max_places)
    fmt = f"{{:.{max_places}f}}"
    s = fmt.format(val).replace(".", "").lstrip("0")
    return s if s else "0"

def forgot_the_decimal_point_applies(p):
    return True

# ---- BATCH B: g5-multiply ----
def forgot_the_placeholder_zero(p):
    a, b = p['a'], p['b']
    return _fmt_num(a * (b % 10) + a * (b // 10))

def forgot_the_placeholder_zero_applies(p):
    return p['b'] // 10 > 0

def multiplied_only_the_ones_digit(p):
    a, b = p['a'], p['b']
    return _fmt_num(a * (b % 10))

def multiplied_only_the_ones_digit_applies(p):
    return p['b'] % 10 > 0

def skipped_the_cross_products(p):
    a, b = p['a'], p['b']
    return _fmt_num((10 * (a // 10)) * (10 * (b // 10)) + (a % 10) * (b % 10))

def skipped_the_cross_products_applies(p):
    return True

def added_instead_of_multiplying(p):
    return _fmt_num(p['a'] + p['b'])

def added_instead_of_multiplying_applies(p):
    return True

def put_the_zero_on_the_wrong_row(p):
    a, b = p['a'], p['b']
    return _fmt_num(a * (b % 10) * 10 + a * (b // 10))

def put_the_zero_on_the_wrong_row_applies(p):
    return True

# ---- BATCH B: g6-fraction-division ----
def multiplied_without_flipping(p):
    return _fmt_frac(Fraction(p['a'] * p['c'], p['b'] * p['d']))

def multiplied_without_flipping_applies(p):
    return True

def flipped_the_first_fraction(p):
    return _fmt_frac(Fraction(p['b'] * p['c'], p['a'] * p['d']))

def flipped_the_first_fraction_applies(p):
    return p['a'] * p['d'] != p['b'] * p['c']

def flipped_both_fractions(p):
    return _fmt_frac(Fraction(p['b'] * p['d'], p['a'] * p['c']))

def flipped_both_fractions_applies(p):
    return p['a'] * p['c'] != p['b'] * p['d']

def added_instead_of_dividing(p):
    return _fmt_frac(Fraction(p['a'], p['b']) + Fraction(p['c'], p['d']))

def added_instead_of_dividing_applies(p):
    return True

RULES: Dict[str, Tuple] = {
    # Pilot
    'added_tops_and_bottoms':        (added_tops_and_bottoms,        added_tops_and_bottoms_applies,        ['g5-fractions-add']),
    'renamed_bottom_kept_tops':      (renamed_bottom_kept_tops,      renamed_bottom_kept_tops_applies,      ['g5-fractions-add']),
    'multiplied_instead_of_adding':  (multiplied_instead_of_adding,  multiplied_instead_of_adding_applies,  ['g5-fractions-add']),
    'subtracted_instead_of_adding':  (subtracted_instead_of_adding,  subtracted_instead_of_adding_applies,  ['g5-fractions-add']),
    'added_tops_kept_first_bottom':  (added_tops_kept_first_bottom,  added_tops_kept_first_bottom_applies,  ['g5-fractions-add']),
    'added_the_sides':               (added_the_sides,               added_the_sides_applies,               ['g5-volume']),
    'found_base_area_only':          (found_base_area_only,          found_base_area_only_applies,          ['g5-volume']),
    'used_surface_area_formula':     (used_surface_area_formula,     used_surface_area_formula_applies,     ['g5-volume']),
    'multiplied_two_sides_then_added_height': (multiplied_two_sides_then_added_height, multiplied_two_sides_then_added_height_applies, ['g5-volume']),
    'cubed_one_side':                (cubed_one_side,                cubed_one_side_applies,                ['g5-volume']),
    'multiplied_by_percent_number':  (multiplied_by_percent_number,  multiplied_by_percent_number_applies,  ['g6-percents']),
    'moved_decimal_wrong_way':       (moved_decimal_wrong_way,       moved_decimal_wrong_way_applies,       ['g6-percents']),
    'found_the_leftover_amount':     (found_the_leftover_amount,     found_the_leftover_amount_applies,     ['g6-percents']),
    'divided_instead_of_multiplying':(divided_instead_of_multiplying,divided_instead_of_multiplying_applies,['g6-percents']),
    'found_one_percent_only':        (found_one_percent_only,        found_one_percent_only_applies,        ['g6-percents']),
    'subtracted_instead_of_dividing':(subtracted_instead_of_dividing,subtracted_instead_of_dividing_applies,['g6-equations']),
    'multiplied_instead_of_dividing':(multiplied_instead_of_dividing,multiplies_instead_of_dividing_applies,['g6-equations', 'g6-unit-rates']),
    'divided_the_wrong_way':         (divided_the_wrong_way,         divided_the_wrong_way_applies,         ['g6-equations']),
    'ignored_the_coefficient':       (ignored_the_coefficient,       ignored_the_coefficient_applies,       ['g6-equations']),
    'added_instead_of_subtracting':  (added_instead_of_subtracting,  added_instead_of_subtracting_applies,  ['g6-equations']),
    'subtracted_the_wrong_way':      (subtracted_the_wrong_way,      subtracted_the_wrong_way_applies,      ['g6-equations']),
    'undid_multiplication_first':    (undid_multiplication_first,    undid_multiplication_first_applies,    ['g6-equations']),
    'added_the_constant':            (added_the_constant,            added_the_constant_applies,            ['g6-equations']),
    'ignored_the_constant_term':     (ignored_the_constant_term,     ignored_the_constant_term_applies,     ['g6-equations']),
    'ignored_the_added_value':       (ignored_the_added_value,       ignored_the_added_value_applies,       ['g6-equations']),
    'used_added_value_as_answer':    (used_added_value_as_answer,    used_added_value_as_answer_applies,    ['g6-equations']),
    'dropped_the_remainder':         (dropped_the_remainder,         dropped_the_remainder_applies,         ['g5-divide']),
    'swapped_quotient_and_remainder':(swapped_quotient_and_remainder,swapped_quotient_and_remainder_applies, ['g5-divide']),
    'stopped_subtracting_too_early': (stopped_subtracting_too_early, stopped_subtracting_too_early_applies,  ['g5-divide']),
    'misplaced_quotient_digit':      (misplaced_quotient_digit,      misplaced_quotient_digit_applies,      ['g5-divide']),
    'rounded_quotient_up_kept_remainder': (rounded_quotient_up_kept_remainder, rounded_quotient_up_kept_remainder_applies, ['g5-divide']),
    # Batch A: g6-ratios
    'additive_ratio_scaling':        (additive_ratio_scaling,        additive_ratio_scaling_applies,        ['g6-ratios']),
    'inverts_ratio_terms_order':     (inverts_ratio_terms_order,     inverts_ratio_terms_order_applies,     ['g6-ratios']),
    'multiplied_only_first_term':    (multiplied_only_first_term,    multiplied_only_first_term_applies,    ['g6-ratios']),
    'part_to_part_vs_part_to_whole': (part_to_part_vs_part_to_whole, part_to_part_vs_part_to_whole_applies, ['g6-ratios']),
    'squared_terms':                 (squared_terms,                 squared_terms_applies,                 ['g6-ratios']),
    # Batch A: g6-unit-rates
    'divides_in_reversed_order':     (divides_in_reversed_order,     divides_in_reversed_order_applies,     ['g6-unit-rates']),
    'forgets_unit_rate_denominator_is_one': (forgets_unit_rate_denominator_is_one, forgets_unit_rate_denominator_is_one_applies, ['g6-unit-rates']),
    'subtracts_quantities':          (subtracts_quantities,          subtracts_quantities_applies,          ['g6-unit-rates']),
    'adds_quantities':               (adds_quantities,               adds_quantities_applies,               ['g6-unit-rates']),
    # Batch A: g5-fractions-multiply
    'added_fractions_instead':       (added_fractions_instead,       added_fractions_instead_applies,       ['g5-fractions-multiply']),
    'cross_multiplies_instead_of_multiplying_straight': (cross_multiplies_instead_of_multiplying_straight, cross_multiplies_instead_of_multiplying_straight_applies, ['g5-fractions-multiply']),
    'multiplies_tops_adds_bottoms':  (multiplies_tops_adds_bottoms,  multiplies_tops_adds_bottoms_applies,  ['g5-fractions-multiply']),
    'added_tops_multiplied_bottoms': (added_tops_multiplied_bottoms, added_tops_multiplied_bottoms_applies, ['g5-fractions-multiply']),
    # Batch A: g6-mean-median
    'finds_median_without_ordering_data': (finds_median_without_ordering_data, finds_median_without_ordering_data_applies, ['g6-mean-median']),
    'confuses_mean_with_median':     (confuses_mean_with_median,     confuses_mean_with_median_applies,     ['g6-mean-median']),
    'gave_the_total_instead_of_the_mean': (gave_the_total_instead_of_the_mean, gave_the_total_instead_of_the_mean_applies, ['g6-mean-median']),
    'finds_range_instead':           (finds_range_instead,           finds_range_instead_applies,           ['g6-mean-median']),
    'ignores_middle_average_for_even_count': (ignores_middle_average_for_even_count, ignores_middle_average_for_even_count_applies, ['g6-mean-median']),
    # Batch B: g5-decimal-ops
    'ignored_the_decimal_point':     (ignored_the_decimal_point,     ignored_the_decimal_point_applies,     ['g5-decimal-ops']),
    'subtracted_smaller_digit_from_larger': (subtracted_smaller_digit_from_larger, subtracted_smaller_digit_from_larger_applies, ['g5-decimal-ops']),
    'dropped_the_carry':             (dropped_the_carry,             dropped_the_carry_applies,             ['g5-decimal-ops']),
    'used_the_wrong_operation':      (used_the_wrong_operation,      used_the_wrong_operation_applies,      ['g5-decimal-ops']),
    'forgot_the_decimal_point':      (forgot_the_decimal_point,      forgot_the_decimal_point_applies,      ['g5-decimal-ops']),
    # Batch B: g5-multiply
    'forgot_the_placeholder_zero':   (forgot_the_placeholder_zero,   forgot_the_placeholder_zero_applies,   ['g5-multiply']),
    'multiplied_only_the_ones_digit':(multiplied_only_the_ones_digit,multiplied_only_the_ones_digit_applies,['g5-multiply']),
    'skipped_the_cross_products':    (skipped_the_cross_products,    skipped_the_cross_products_applies,    ['g5-multiply']),
    'added_instead_of_multiplying':  (added_instead_of_multiplying,  added_instead_of_multiplying_applies,  ['g5-multiply']),
    'put_the_zero_on_the_wrong_row': (put_the_zero_on_the_wrong_row, put_the_zero_on_the_wrong_row_applies, ['g5-multiply']),
    # Batch B: g6-fraction-division
    'multiplied_without_flipping':   (multiplied_without_flipping,   multiplied_without_flipping_applies,   ['g6-fraction-division']),
    'flipped_the_first_fraction':    (flipped_the_first_fraction,    flipped_the_first_fraction_applies,    ['g6-fraction-division']),
    'flipped_both_fractions':        (flipped_both_fractions,        flipped_both_fractions_applies,        ['g6-fraction-division']),
    'added_instead_of_dividing':     (added_instead_of_dividing,     added_instead_of_dividing_applies,     ['g6-fraction-division']),
}

def apply_rule(tag: str, params: dict) -> Optional[str]:
    if tag not in RULES:
        return None
    fn, applies_fn, _ = RULES[tag]
    if not applies_fn(params):
        return None
    return fn(params)

def get_topic_rules(topic_id: str) -> list:
    return [tag for tag, (_, _, topics) in RULES.items() if topic_id in topics]

