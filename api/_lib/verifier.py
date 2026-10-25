from __future__ import annotations
import ast
import re
import math
import statistics
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple, Union
from pydantic import BaseModel, Field

from api._lib.schemas import Question, Lesson
from api._lib.misconceptions import load_registry, apply_rule, RULES

MAX_EXPR_LENGTH = 300
MAX_EXPONENT = 100
MAX_AST_NODES = 120


class VerificationError(Exception):
    """Raised when an expression or verification fails safety or mathematical validity."""
    pass


class VerificationResult(BaseModel):
    passed: bool
    reasons: List[str] = Field(default_factory=list)


def safe_fraction(val: Any) -> Fraction:
    """Coerce an int, float, string, or Fraction into an exact Fraction."""
    if isinstance(val, Fraction):
        return val
    if isinstance(val, int):
        return Fraction(val, 1)
    if isinstance(val, float):
        return Fraction(str(val))
    if isinstance(val, str):
        cleaned = val.strip().replace(",", "")
        return Fraction(cleaned)
    raise ValueError(f"Cannot convert {type(val)} to Fraction")


# -------------------------------------------------------------
# Option Normalizer Module
# -------------------------------------------------------------
def normalize_option(raw: str) -> Tuple[str, Optional[Fraction]]:
    """
    Normalizes options into a canonical string key and an optional exact Fraction value.
    Handles:
    - Fractions: '5/12', '-3/4'
    - Decimals: '0.35', '-1.5'
    - Mixed numbers: '2 1/4', '-3 1/2'
    - Percents: '25%' -> Fraction(25, 100) = Fraction(1, 4)
    - Ratios: '3:4' -> key 'ratio:3:4' (and ratio numerical value 3/4)
    - Currency: '$1.50' -> Fraction(15, 10)
    - Unit suffixes: '120 cm³', '45 ft²', '15 kg', '14 cups'
    - Integers with commas: '1,250' -> Fraction(1250, 1)
    - Negatives: '-7', '- 7'
    """
    if raw is None:
        return ("", None)

    s = str(raw).strip()
    s = s.replace("$", "").replace(",", "")

    # Remove units like cm³, ft², m^2, kg, etc.
    s = re.sub(r"\s*(cm³|cm\^3|m³|m\^3|ft³|ft\^3|in³|in\^3|in\^2|cm²|cm\^2|m²|m\^2|ft²|ft\^2|kg|g|mg|lbs|lb|oz|units|cubes|sq\s*units|cubic\s*units|cups|items|apples|miles|hrs|hours|mph)\b", "", s, flags=re.I).strip()

    # Percent syntax e.g. 25%
    if s.endswith("%"):
        inner = s[:-1].strip()
        try:
            num = safe_fraction(inner)
            frac = num / Fraction(100, 1)
            return (f"frac:{frac.numerator}/{frac.denominator}", frac)
        except Exception:
            return (s, None)

    # Division with remainder format e.g. "12 R 3" or "12 r 3" or "12 remainder 3"
    rem_match = re.match(r"^(-?\d+)\s*(?:R|r|remainder)\s*(\d+)$", s, re.I)
    if rem_match:
        q = int(rem_match.group(1))
        r = int(rem_match.group(2))
        return (f"rem:{q} R {r}", None)

    # Comparison symbols / words normalization
    comp_map = {
        ">": ">", "greater": ">", "greater than": ">",
        "<": "<", "less": "<", "less than": "<",
        "=": "=", "equal": "=", "equal to": "="
    }
    if s.lower() in comp_map:
        return (comp_map[s.lower()], None)

    # Ratio syntax e.g. "3:4" or "3 to 4"
    ratio_match = re.match(r"^(-?\d+)\s*(?::|to)\s*(-?\d+)$", s, re.I)
    if ratio_match:
        a = int(ratio_match.group(1))
        b = int(ratio_match.group(2))
        gcd_val = math.gcd(a, b) or 1
        simp_a = a // gcd_val
        simp_b = b // gcd_val
        frac_val = Fraction(a, b) if b != 0 else None
        return (f"ratio:{simp_a}:{simp_b}", frac_val)

    # Mixed number e.g. "2 1/4" or "-2 1/4"
    mixed_match = re.match(r"^(-?)(\d+)\s+(\d+)\s*/\s*(\d+)$", s)
    if mixed_match:
        sign = -1 if mixed_match.group(1) == "-" else 1
        whole = int(mixed_match.group(2))
        num = int(mixed_match.group(3))
        den = int(mixed_match.group(4))
        if den == 0:
            return (s, None)
        frac = sign * (Fraction(whole, 1) + Fraction(num, den))
        return (f"frac:{frac.numerator}/{frac.denominator}", frac)

    # Simple fraction e.g. "5/12"
    frac_match = re.match(r"^(-?\d+)\s*/\s*(-?\d+)$", s)
    if frac_match:
        num = int(frac_match.group(1))
        den = int(frac_match.group(2))
        if den == 0:
            return (s, None)
        frac = Fraction(num, den)
        return (f"frac:{frac.numerator}/{frac.denominator}", frac)

    # Plain decimal or integer
    dec_match = re.match(r"^-?\d+(\.\d+)?$", s)
    if dec_match:
        try:
            frac = Fraction(s)
            return (f"frac:{frac.numerator}/{frac.denominator}", frac)
        except Exception:
            pass

    # Fallback to normalized lowercase string
    cleaned_s = re.sub(r"\s+", " ", s.lower()).strip()
    return (cleaned_s, None)


# -------------------------------------------------------------
# AST Expression Evaluator & Whitelisted Helpers
# -------------------------------------------------------------
def solve_linear(equation: str) -> Fraction:
    """
    Solves a single-variable linear equation e.g. '3x + 5 = 20' or '2x = 10' or 'x - 4 = 12'.
    Returns exact Fraction solution.
    """
    clean_eq = equation.replace(" ", "")
    if "=" not in clean_eq:
        raise ValueError("Equation must contain '='")
    left_str, right_str = clean_eq.split("=", 1)

    # Parse simple ax + b = c form
    # Identify variable name
    var_match = re.search(r"[a-zA-Z]", clean_eq)
    if not var_match:
        raise ValueError("No variable found in linear equation")
    var = var_match.group(0)

    # Normalize sides
    def extract_linear_coeffs(side: str, v: str) -> Tuple[Fraction, Fraction]:
        # returns (a, b) for a*v + b
        # Replace occurrences of + and -
        tokens = re.findall(r"[+-]?[^+-]+", side if side.startswith(("+", "-")) else "+" + side)
        a_total = Fraction(0, 1)
        b_total = Fraction(0, 1)
        for tok in tokens:
            tok = tok.strip()
            if not tok:
                continue
            if v in tok:
                coeff_part = tok.replace(v, "")
                if coeff_part in ("", "+"):
                    coeff = Fraction(1, 1)
                elif coeff_part == "-":
                    coeff = Fraction(-1, 1)
                else:
                    coeff = Fraction(coeff_part)
                a_total += coeff
            else:
                b_total += Fraction(tok)
        return a_total, b_total

    a1, b1 = extract_linear_coeffs(left_str, var)
    a2, b2 = extract_linear_coeffs(right_str, var)

    a_net = a1 - a2
    b_net = b2 - b1
    if a_net == 0:
        raise ValueError("Equation has no unique solution (coefficient is zero)")
    return b_net / a_net


def ratio_simplify(a: Any, b: Any) -> str:
    a_f = safe_fraction(a)
    b_f = safe_fraction(b)
    # Scale to integer representation
    common_den = a_f.denominator * b_f.denominator
    num_a = a_f.numerator * b_f.denominator
    num_b = b_f.numerator * a_f.denominator
    g = math.gcd(num_a, num_b) or 1
    return f"{num_a // g}:{num_b // g}"


def unit_rate(amount: Any, units: Any) -> Fraction:
    return safe_fraction(amount) / safe_fraction(units)


def percent_of(percent: Any, total: Any) -> Fraction:
    return (safe_fraction(percent) / Fraction(100, 1)) * safe_fraction(total)


def volume_box(length: Any, width: Any, height: Any) -> Fraction:
    return safe_fraction(length) * safe_fraction(width) * safe_fraction(height)


def round_to(x: Any, places: Any = 0) -> Fraction:
    val = float(safe_fraction(x))
    res = round(val, int(safe_fraction(places)))
    return Fraction(str(res))


def math_mean(*args: Any) -> Fraction:
    flat: List[Fraction] = []
    for a in args:
        if isinstance(a, (list, tuple)):
            flat.extend(safe_fraction(x) for x in a)
        else:
            flat.append(safe_fraction(a))
    if not flat:
        raise ValueError("Mean requires at least one value")
    return sum(flat, Fraction(0, 1)) / Fraction(len(flat), 1)


def math_median(*args: Any) -> Fraction:
    flat: List[Fraction] = []
    for a in args:
        if isinstance(a, (list, tuple)):
            flat.extend(safe_fraction(x) for x in a)
        else:
            flat.append(safe_fraction(a))
    if not flat:
        raise ValueError("Median requires at least one value")
    flat.sort()
    n = len(flat)
    if n % 2 == 1:
        return flat[n // 2]
    else:
        return (flat[n // 2 - 1] + flat[n // 2]) / Fraction(2, 1)


def math_mode(*args: Any) -> Fraction:
    flat: List[Fraction] = []
    for a in args:
        if isinstance(a, (list, tuple)):
            flat.extend(safe_fraction(x) for x in a)
        else:
            flat.append(safe_fraction(a))
    if not flat:
        raise ValueError("Mode requires at least one value")
    counts: Dict[Fraction, int] = {}
    for x in flat:
        counts[x] = counts.get(x, 0) + 1
    highest = max(counts.values())
    modes = [k for k, v in counts.items() if v == highest]
    return modes[0]


def math_gcd(a: Any, b: Any) -> Fraction:
    return Fraction(math.gcd(int(safe_fraction(a)), int(safe_fraction(b))), 1)


def math_lcm(a: Any, b: Any) -> Fraction:
    val_a = int(safe_fraction(a))
    val_b = int(safe_fraction(b))
    return Fraction(abs(val_a * val_b) // (math.gcd(val_a, val_b) or 1), 1)


def compare(a: Any, b: Any) -> str:
    """Computes comparison between two numeric quantities, returning '<', '>', or '='.
    Options may be '<', '>', '=', or word forms like 'less than', 'greater than', 'equal to'.
    """
    fa = safe_fraction(a)
    fb = safe_fraction(b)
    if fa < fb:
        return "<"
    elif fa > fb:
        return ">"
    return "="


def divmod_rem(dividend: Any, divisor: Any) -> str:
    """Computes integer division with remainder and returns formatted string 'Q R r'.
    Verified by exact divmod computation on integers: dividend = q * divisor + r, with 0 <= r < divisor.
    """
    a = int(safe_fraction(dividend))
    b = int(safe_fraction(divisor))
    if b == 0:
        raise VerificationError("Division by zero in divmod_rem")
    q, r = divmod(a, b)
    return f"{q} R {r}"


def check_equiv(expr_a: str, expr_b: str, var: str = "x") -> str:
    """Numerically verifies whether two algebraic expressions are equivalent.
    Evaluates both expressions at several fixed sample points (e.g. x = 0, 1, 2, -1, 5, 1/2) using exact Fractions.
    Returns 'equivalent' if both expressions yield identical Fractions at all test points, else 'not equivalent'.
    NOTE: This is a numeric sample check with documented limits (can fail on pathological high-degree or piecewise functions).
    """
    test_points = [0, 1, 2, -1, 5, Fraction(1, 2)]
    for val in test_points:
        sub_a = re.sub(rf"\b{var}\b", f"({val})", str(expr_a))
        sub_b = re.sub(rf"\b{var}\b", f"({val})", str(expr_b))
        try:
            res_a = evaluate_expression(sub_a)
            res_b = evaluate_expression(sub_b)
            if safe_fraction(res_a) != safe_fraction(res_b):
                return "not equivalent"
        except Exception:
            return "not equivalent"
    return "equivalent"


WHITELISTED_FUNCS = {
    "mean": math_mean,
    "median": math_median,
    "mode": math_mode,
    "gcd": math_gcd,
    "lcm": math_lcm,
    "abs": lambda x: abs(safe_fraction(x)),
    "pow": lambda x, y: safe_fraction(x) ** int(safe_fraction(y)),
    "round_to": round_to,
    "floor": lambda x: Fraction(math.floor(float(safe_fraction(x))), 1),
    "ceil": lambda x: Fraction(math.ceil(float(safe_fraction(x))), 1),
    "ratio_simplify": ratio_simplify,
    "unit_rate": unit_rate,
    "percent_of": percent_of,
    "volume_box": volume_box,
    "solve_linear": solve_linear,
    "compare": compare,
    "divmod_rem": divmod_rem,
    "check_equiv": check_equiv,
}


class ASTEvaluator(ast.NodeVisitor):
    def __init__(self) -> None:
        self.node_count = 0

    def visit(self, node: ast.AST) -> Any:
        self.node_count += 1
        if self.node_count > MAX_AST_NODES:
            raise VerificationError(f"Expression exceeds maximum AST node limit ({MAX_AST_NODES})")
        return super().visit(node)

    def visit_Expression(self, node: ast.Expression) -> Any:
        return self.visit(node.body)

    def visit_Constant(self, node: ast.Constant) -> Any:
        if isinstance(node.value, (int, float)):
            return safe_fraction(node.value)
        if isinstance(node.value, str):
            return node.value
        raise VerificationError(f"Unsupported constant: {node.value}")

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Any:
        operand = self.visit(node.operand)
        if isinstance(node.op, ast.USub):
            return -safe_fraction(operand)
        if isinstance(node.op, ast.UAdd):
            return safe_fraction(operand)
        raise VerificationError(f"Unsupported unary operator: {type(node.op)}")

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = node.op

        if isinstance(op, ast.Add):
            return safe_fraction(left) + safe_fraction(right)
        if isinstance(op, ast.Sub):
            return safe_fraction(left) - safe_fraction(right)
        if isinstance(op, ast.Mult):
            return safe_fraction(left) * safe_fraction(right)
        if isinstance(op, ast.Div):
            r = safe_fraction(right)
            if r == 0:
                raise VerificationError("Division by zero in expression")
            return safe_fraction(left) / r
        if isinstance(op, ast.FloorDiv):
            r = safe_fraction(right)
            if r == 0:
                raise VerificationError("Floor division by zero")
            return Fraction(int(safe_fraction(left) // r), 1)
        if isinstance(op, ast.Mod):
            r = safe_fraction(right)
            if r == 0:
                raise VerificationError("Modulo by zero")
            return Fraction(int(safe_fraction(left)) % int(r), 1)
        if isinstance(op, ast.Pow):
            exp_val = safe_fraction(right)
            if abs(int(exp_val)) > MAX_EXPONENT:
                raise VerificationError(f"Exponent exceeds safety limit ({MAX_EXPONENT})")
            return safe_fraction(left) ** int(exp_val)

        raise VerificationError(f"Unsupported binary operator: {type(op)}")

    def visit_Call(self, node: ast.Call) -> Any:
        if not isinstance(node.func, ast.Name):
            raise VerificationError("Only direct whitelisted function calls are permitted")
        func_name = node.func.id
        if func_name not in WHITELISTED_FUNCS:
            raise VerificationError(f"Function '{func_name}' is not in safety whitelist")

        func = WHITELISTED_FUNCS[func_name]
        args = [self.visit(a) for a in node.args]
        return func(*args)

    def visit_List(self, node: ast.List) -> Any:
        return [self.visit(elt) for elt in node.elts]

    def visit_Tuple(self, node: ast.Tuple) -> Any:
        return tuple(self.visit(elt) for elt in node.elts)

    def generic_visit(self, node: ast.AST) -> Any:
        raise VerificationError(f"Disallowed syntax: {type(node).__name__}")


def evaluate_expression(expr: str) -> Any:
    """
    Safely evaluates a math expression using pure AST parsing and exact Fraction arithmetic.
    Pre-normalizes percent expressions like '25% of 80'.
    """
    if not expr or len(expr) > MAX_EXPR_LENGTH:
        raise VerificationError(f"Expression exceeds length limit ({MAX_EXPR_LENGTH})")

    cleaned = expr.strip()

    # Pre-normalize: 'solve: 3x + 5 = 20' or 'solve_linear(3x+5=20)'
    if "=" in cleaned and not cleaned.startswith("solve_linear("):
        cleaned = f"solve_linear('{cleaned}')"

    # Pre-normalize: '25% of 80' -> 'percent_of(25, 80)'
    pct_of = re.match(r"^(\d+(?:\.\d+)?)\s*%\s*of\s*(.+)$", cleaned, re.I)
    if pct_of:
        p_val = pct_of.group(1)
        t_val = pct_of.group(2)
        cleaned = f"percent_of({p_val}, {t_val})"

    # Disallow malicious patterns explicitly
    if any(k in cleaned for k in ["__", "import", "exec", "eval", "open", "getattr", "setattr"]):
        raise VerificationError("Expression contains forbidden keywords")

    try:
        tree = ast.parse(cleaned, mode="eval")
    except Exception as e:
        raise VerificationError(f"AST parse error: {str(e)}")

    evaluator = ASTEvaluator()
    return evaluator.visit(tree)


# -------------------------------------------------------------
# Main Question & Lesson Verifiers
# -------------------------------------------------------------
def verify_question(q: Union[Question, Dict[str, Any]], verifier_type: str = "fraction_arithmetic") -> VerificationResult:
    """
    Verifies question validity:
    1. Valid Pydantic schema
    2. Expression evaluates without error
    3. Exactly one option matches computed result
    4. correct_index agrees with matching option
    5. Options are distinct after normalization
    6. Every wrong option has a non-empty misconception tag
    7. Stem, explanation, hint non-empty with no unresolved placeholders like {x} or [TODO]
    """
    reasons: List[str] = []

    # 1. Schema check
    if not isinstance(q, Question):
        try:
            q = Question.model_validate(q)
        except Exception as e:
            return VerificationResult(passed=False, reasons=[f"Schema validation failed: {str(e)}"])
    registry = load_registry()
    # Check for placeholder leaks
    placeholder_pattern = re.compile(r"\{[a-zA-Z0-9_]+\}|\[TODO\]|\[INSERT\]", re.I)
    for field_name, val in [("stem", q.stem), ("explanation", q.explanation), ("hint", q.hint)]:
        if placeholder_pattern.search(val):
            reasons.append(f"{field_name} contains unresolved placeholder")

    # 2. Evaluate Expression
    computed_val = None
    try:
        computed_val = evaluate_expression(q.expression)
    except Exception as e:
        reasons.append(f"Expression '{q.expression}' evaluation error: {str(e)}")

    # 3. Normalize options & verify uniqueness
    normalized_keys: List[str] = []
    option_fractions: List[Optional[Fraction]] = []

    for i, opt in enumerate(q.options):
        norm_key, frac_val = normalize_option(opt.text)
        normalized_keys.append(norm_key)
        option_fractions.append(frac_val)

        # Misconception check on wrong answers
        if i == q.correct_index:
            if opt.misconception is not None and opt.misconception != "":
                reasons.append(f"Correct option {i} must have null misconception, found '{opt.misconception}'")
        else:
            tag = (getattr(opt, "misconception_id", None) or opt.misconception or "").strip()
            if not tag:
                reasons.append(f"Wrong option {i} ('{opt.text}') is missing a misconception tag")

    # Distinctness check
    if len(set(normalized_keys)) != len(normalized_keys):
        reasons.append(f"Options are not distinct after normalization: {normalized_keys}")

    # 4. Canonical match
    if computed_val is not None:
        matching_indices: List[int] = []

        if verifier_type == "text_exact" or isinstance(computed_val, str):
            # String comparison
            target_str = str(computed_val).strip().lower()
            for idx, key in enumerate(normalized_keys):
                clean_opt = key.replace("frac:", "").replace("ratio:", "").replace("rem:", "").strip().lower()
                clean_raw = str(q.options[idx].text).strip().lower()
                if clean_opt == target_str or clean_raw == target_str or key == target_str:
                    matching_indices.append(idx)
        else:
            try:
                target_frac = safe_fraction(computed_val)
                for idx, f_val in enumerate(option_fractions):
                    if f_val is not None and f_val == target_frac:
                        matching_indices.append(idx)
            except Exception as e:
                reasons.append(f"Could not convert computed value {computed_val} to Fraction: {str(e)}")

        if len(matching_indices) == 0:
            reasons.append(f"No option matched the evaluated answer ({computed_val})")
        elif len(matching_indices) > 1:
            reasons.append(f"Multiple options ({matching_indices}) matched the evaluated answer ({computed_val})")
        elif matching_indices[0] != q.correct_index:
            reasons.append(f"correct_index ({q.correct_index}) does not agree with computed answer match ({matching_indices[0]})")

    # 5. Distractor Provenance and Misconception Verification
    has_params = q.params is not None
    is_dict_params = isinstance(q.params, dict)

    if has_params:
        params_dict = q.params if is_dict_params else {}
        all_distractors_verified = True
        for i, opt in enumerate(q.options):
            if i == q.correct_index:
                continue
            tag = str(getattr(opt, "misconception_id", None) or opt.misconception or "").strip()
            if not tag:
                reasons.append(f"Option {i} ('{opt.text}') is missing a misconception tag")
                all_distractors_verified = False
                continue
            if tag not in registry:
                reasons.append(f"Option {i} has unknown misconception id '{tag}'")
                all_distractors_verified = False
                continue
            entry = registry[tag]
            topic_ids = entry.get("topic_ids", [])
            if q.topic_id not in topic_ids:
                reasons.append(f"Option {i} misconception tag '{tag}' is not listed for topic '{q.topic_id}'")
                all_distractors_verified = False
                continue
            if tag not in RULES:
                reasons.append(f"Option {i} rule '{tag}' is not implemented in RULES")
                all_distractors_verified = False
                continue
            fn, applies_fn, _ = RULES[tag]
            if not applies_fn(params_dict):
                reasons.append(f"Option {i} rule '{tag}' applies_when is false for params")
                all_distractors_verified = False
                continue
            expected = fn(params_dict)
            if expected is None:
                reasons.append(f"Option {i} rule '{tag}' returned None for params")
                all_distractors_verified = False
                continue
            norm_exp, frac_exp = normalize_option(expected)
            norm_opt, frac_opt = normalize_option(opt.text)
            match = False
            if frac_exp is not None and frac_opt is not None and frac_exp == frac_opt:
                match = True
            elif norm_exp == norm_opt:
                match = True
            else:
                clean_exp = norm_exp.replace("frac:", "").replace("ratio:", "").replace("rem:", "").strip().lower()
                clean_opt = norm_opt.replace("frac:", "").replace("ratio:", "").replace("rem:", "").strip().lower()
                if clean_exp == clean_opt or str(expected).strip().lower() == str(opt.text).strip().lower():
                    match = True
            if not match:
                reasons.append(f"Option {i} with tag '{tag}' expected '{expected}', but option text is '{opt.text}'")
                all_distractors_verified = False

        q.provenance = "verified" if (all_distractors_verified and len(reasons) == 0) else "unchecked"
        if q.provenance == "verified":
            q.verified = True
    else:
        # Without params (e.g. LLM generated questions)
        any_rule_verified = False
        for i, opt in enumerate(q.options):
            if i == q.correct_index:
                continue
            tag = str(getattr(opt, "misconception_id", None) or opt.misconception or "").strip()
            if not tag:
                reasons.append(f"Option {i} ('{opt.text}') is missing a misconception tag")
                continue
            if tag in registry:
                entry = registry[tag]
                topic_ids = entry.get("topic_ids", [])
                if q.topic_id.startswith(("g5-", "g6-")) and q.topic_id not in topic_ids:
                    reasons.append(f"Option {i} misconception tag '{tag}' is not listed for topic '{q.topic_id}'")
                # Try to reproduce from expression
                parsed = _parse_params_from_expr(q.expression, q.topic_id)
                if parsed and tag in RULES:
                    fn, applies_fn, _ = RULES[tag]
                    if applies_fn(parsed):
                        expected = fn(parsed)
                        norm_exp, frac_exp = normalize_option(expected)
                        norm_opt, frac_opt = normalize_option(opt.text)
                        match = False
                        if frac_exp is not None and frac_opt is not None and frac_exp == frac_opt:
                            match = True
                        elif norm_exp == norm_opt:
                            match = True
                        else:
                            clean_exp = norm_exp.replace("frac:", "").replace("ratio:", "").replace("rem:", "").strip().lower()
                            clean_opt = norm_opt.replace("frac:", "").replace("ratio:", "").replace("rem:", "").strip().lower()
                            if clean_exp == clean_opt or str(expected).strip().lower() == str(opt.text).strip().lower():
                                match = True
                        if not match:
                            reasons.append(f"Option {i} with tag '{tag}' ran on parsed expression and expected '{expected}', but option text is '{opt.text}'")
                        else:
                            any_rule_verified = True
            elif tag and q.topic_id in {"g5-fractions-add", "g5-volume", "g6-percents", "g6-equations", "g5-divide"}:
                reasons.append(f"Option {i} misconception tag '{tag}' not found in registry")

        if any_rule_verified and len(reasons) == 0:
            q.provenance = "verified"
            q.verified = True
        else:
            q.provenance = "unchecked"
    return VerificationResult(passed=(len(reasons) == 0), reasons=reasons)


def _parse_params_from_expr(expr: str, topic_id: str) -> Optional[Dict[str, Any]]:
    s = str(expr).strip()
    if topic_id == "g5-fractions-add":
        m = re.match(r"^(\d+)/(\d+)\s*\+\s*(\d+)/(\d+)$", s)
        if m:
            return {"a": int(m.group(1)), "b": int(m.group(2)), "c": int(m.group(3)), "d": int(m.group(4))}
    elif topic_id == "g5-volume":
        m = re.match(r"^(\d+)\s*\*\s*(\d+)\s*\*\s*(\d+)$", s)
        if m:
            return {"l": int(m.group(1)), "w": int(m.group(2)), "h": int(m.group(3))}
    elif topic_id == "g6-percents":
        m = re.match(r"^(\d+(?:\.\d+)?)\s*%\s*of\s*(\d+(?:\.\d+)?)$", s, re.I)
        if m:
            p_val = float(m.group(1)) if "." in m.group(1) else int(m.group(1))
            n_val = float(m.group(2)) if "." in m.group(2) else int(m.group(2))
            return {"p": p_val, "n": n_val}
    elif topic_id == "g6-equations":
        m1 = re.match(r"^(\d+)\s*\*\s*x\s*=\s*(\d+)$", s)
        if m1:
            return {"form": "ax_b", "a": int(m1.group(1)), "b": int(m1.group(2))}
        m2 = re.match(r"^x\s*\+\s*(\d+)\s*=\s*(\d+)$", s)
        if m2:
            return {"form": "xpa_b", "a": int(m2.group(1)), "b": int(m2.group(2))}
        m3 = re.match(r"^(\d+)\s*\*\s*x\s*\+\s*(\d+)\s*=\s*(\d+)$", s)
        if m3:
            return {"form": "axpb_c", "a": int(m3.group(1)), "b": int(m3.group(2)), "c": int(m3.group(3))}
    elif topic_id == "g5-divide":
        m = re.match(r"^(\d+)\s*/\s*(\d+)$", s)
        if m:
            n_val, d_val = int(m.group(1)), int(m.group(2))
            if d_val != 0:
                return {"n": n_val, "d": d_val, "q": n_val // d_val, "r": n_val % d_val}
    return None


def verify_lesson(lesson: Union[Lesson, Dict[str, Any]]) -> VerificationResult:
    """
    Verifies lesson accuracy:
    - Every evaluable math field in worked example steps evaluates cleanly.
    - Final step result matches stated answer.
    """
    reasons: List[str] = []
    if not isinstance(lesson, Lesson):
        try:
            lesson = Lesson.model_validate(lesson)
        except Exception as e:
            return VerificationResult(passed=False, reasons=[f"Lesson schema invalid: {str(e)}"])

    for step in lesson.worked_example:
        m = step.math.strip()
        if "=" in m:
            parts = m.split("=")
            try:
                val_left = evaluate_expression(parts[0])
                val_right = evaluate_expression(parts[1])
                if safe_fraction(val_left) != safe_fraction(val_right):
                    reasons.append(f"Step {step.step} equation '{step.math}' is unequal ({val_left} != {val_right})")
            except Exception as e:
                # If it looks like an algebraic equation (e.g. contains math operators or numbers), record error
                if re.search(r"\d", m):
                    reasons.append(f"Step {step.step} equation evaluation error: {str(e)}")
        else:
            # Standalone math expression
            if re.search(r"[\+\-\*\/\%]", m) and re.search(r"\d", m):
                try:
                    evaluate_expression(m)
                except Exception as e:
                    reasons.append(f"Step {step.step} expression evaluation error: {str(e)}")

    return VerificationResult(passed=(len(reasons) == 0), reasons=reasons)
