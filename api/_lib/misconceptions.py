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
def multiplied_instead_of_dividing_applies(p): return p.get('form') == 'ax_b'

def divided_the_wrong_way(p): return _fmt_frac(Fraction(p['a'], p['b']))
def divided_the_wrong_way_applies(p): return p.get('form') == 'ax_b'

def ignored_the_coefficient(p): return _fmt_num(p['b'])
def ignored_the_coefficient_applies(p): return p.get('form') == 'ax_b'

def added_instead_of_subtracting(p): return _fmt_num(p['a'] + p['b'])
def added_instead_of_subtracting_applies(p): return p.get('form') == 'xpa_b'

def subtracted_the_wrong_way(p): return _fmt_num(p['a'] - p['b'])
def subtracted_the_wrong_way_applies(p):
    return p.get('form') == 'xpa_b' and (p['a'] - p['b']) != (p['b'] - p['a'])

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

RULES: Dict[str, Tuple] = {
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
    'multiplied_instead_of_dividing':(multiplied_instead_of_dividing,multiplied_instead_of_dividing_applies,['g6-equations']),
    'divided_the_wrong_way':         (divided_the_wrong_way,         divided_the_wrong_way_applies,         ['g6-equations']),
    'ignored_the_coefficient':       (ignored_the_coefficient,       ignored_the_coefficient_applies,       ['g6-equations']),
    'added_instead_of_subtracting':  (added_instead_of_subtracting,  added_instead_of_subtracting_applies,  ['g6-equations']),
    'subtracted_the_wrong_way':      (subtracted_the_wrong_way,      subtracted_the_wrong_way_applies,      ['g6-equations']),
    'undid_multiplication_first':    (undid_multiplication_first,    undid_multiplication_first_applies,    ['g6-equations']),
    'added_the_constant':            (added_the_constant,            added_the_constant_applies,            ['g6-equations']),
    'ignored_the_constant_term':     (ignored_the_constant_term,     ignored_the_constant_term_applies,     ['g6-equations']),
    'dropped_the_remainder':         (dropped_the_remainder,         dropped_the_remainder_applies,         ['g5-divide']),
    'swapped_quotient_and_remainder':(swapped_quotient_and_remainder,swapped_quotient_and_remainder_applies, ['g5-divide']),
    'stopped_subtracting_too_early': (stopped_subtracting_too_early, stopped_subtracting_too_early_applies,  ['g5-divide']),
    'misplaced_quotient_digit':      (misplaced_quotient_digit,      misplaced_quotient_digit_applies,      ['g5-divide']),
    'rounded_quotient_up_kept_remainder': (rounded_quotient_up_kept_remainder, rounded_quotient_up_kept_remainder_applies, ['g5-divide']),
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
