"""Hand-authored lessons, infographics, and explainer generator for Math Quest.

Builds:
1. data/lessons/<topic_id>.json for ALL 20 topics matching Lesson schema.
   - All evaluable math fields pass api._lib.verifier.verify_lesson.
   - Grade 5 reading level, plain language, clear explanations.
   - Common mistakes drawn from topic misconceptions.
2. data/infographics/<topic_id>.json for the 3 flagship topics:
   - g5-fractions-add
   - g6-ratios
   - g5-volume
3. data/explainers/<topic_id>.json for the 3 flagship topics (6-8 slides each).
"""

from __future__ import annotations
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api._lib.schemas import Lesson, WorkedStep, InfographicData, InfographicStep, ExplainerScript, Slide
from api._lib.verifier import verify_lesson


ALL_LESSONS = {
    "g5-place-value": {
        "title": "Powers of Ten and Place Value Shifts",
        "big_idea": "Each place value is ten times greater than the place to its right and one-tenth of the place to its left.",
        "explanation": "When you multiply a whole number by 10, every digit shifts one place to the left, which adds a zero in the ones place. Multiplying by 100 shifts digits two places to the left. Dividing by 10 shifts digits one place to the right.",
        "worked_example": [
            {"step": 1, "text": "Start with 45 and multiply by 10", "math": "45 * 10 = 450"},
            {"step": 2, "text": "Multiply the new value by 10 again to see a shift of 100", "math": "450 * 10 = 4500"},
            {"step": 3, "text": "Check that 45 times 100 matches", "math": "45 * 100 = 4500"}
        ],
        "key_vocab": ["Place Value", "Power of Ten", "Tenths", "Hundredths", "Shift"],
        "real_world_example": "If 1 gold coin buys 10 arrows, then 45 gold coins buy 45 * 10 = 450 arrows.",
        "common_mistakes": [
            "Adding the number 10 instead of multiplying by 10.",
            "Adding zeros without understanding that digits shifted to higher place values.",
            "Moving the decimal point in the wrong direction when multiplying."
        ]
    },
    "g5-decimal-ops": {
        "title": "Adding and Subtracting Decimals",
        "big_idea": "Always align decimal points so you add or subtract digits with the same place value.",
        "explanation": "Decimals represent parts of a whole. When adding or subtracting, line up tenths with tenths, hundredths with hundredths, and ones with ones. If one decimal has fewer digits, pad it with a zero placeholder.",
        "worked_example": [
            {"step": 1, "text": "Write numbers lining up decimal points for 3.40 and 1.25", "math": "3.4 + 1.25"},
            {"step": 2, "text": "Add tenths and hundredths column by column", "math": "3.40 + 1.25 = 4.65"},
            {"step": 3, "text": "Verify the sum", "math": "4.65 = 4.65"}
        ],
        "key_vocab": ["Decimal Point", "Tenths", "Hundredths", "Placeholder Zero", "Regrouping"],
        "real_world_example": "Buying a magic quill for $3.40 and ink for $1.25 costs $4.65 in total.",
        "common_mistakes": [
            "Aligning digits to the right margin instead of lining up the decimal points.",
            "Forgetting to write a zero placeholder when subtracting shorter decimals.",
            "Treating the decimal point like a wall that stops regrouping."
        ]
    },
    "g5-decimal-compare-round": {
        "title": "Comparing and Rounding Decimals",
        "big_idea": "Compare decimals from left to right starting at the highest place value, and round using the next digit to the right.",
        "explanation": "To compare two decimals, check the whole numbers first, then tenths, then hundredths. A longer decimal is not automatically larger: 0.5 is greater than 0.125 because 5 tenths is greater than 1 tenth. When rounding, look at the digit to the right: 5 or more rounds up, 4 or less stays the same.",
        "worked_example": [
            {"step": 1, "text": "Compare tenths for 0.5 and 0.45", "math": "0.5 > 0.45"},
            {"step": 2, "text": "Round 3.47 to the nearest tenth by looking at 7", "math": "3.5 = 3.5"},
            {"step": 3, "text": "Check rounding difference", "math": "3.5 - 3.47 = 0.03"}
        ],
        "key_vocab": ["Compare", "Round", "Tenths", "Hundredths", "Thousandths"],
        "real_world_example": "A running timer showing 12.4 seconds is faster than 12.45 seconds.",
        "common_mistakes": [
            "Assuming a decimal with more digits is always larger (e.g., thinking 0.125 > 0.5).",
            "Dropping digits instead of using rounding rules.",
            "Comparing hundredths digits before comparing tenths."
        ]
    },
    "g5-fractions-add": {
        "title": "Adding and Subtracting Fractions with Unlike Denominators",
        "big_idea": "Fractions can only be combined directly when they share a common denominator.",
        "explanation": "When fractions have different denominators, find equivalent fractions with a common denominator first. Multiply the numerator and denominator by the same factor so each whole has equal size parts, then add the numerators.",
        "worked_example": [
            {"step": 1, "text": "Find common denominator for 1/2 and 1/3 (common denominator is 6)", "math": "1/2 + 1/3"},
            {"step": 2, "text": "Rename fractions: 1/2 = 3/6 and 1/3 = 2/6", "math": "3/6 + 2/6 = 5/6"},
            {"step": 3, "text": "Confirm the combined sum", "math": "5/6 = 5/6"}
        ],
        "key_vocab": ["Numerator", "Denominator", "Common Denominator", "Equivalent Fraction", "Simplify"],
        "real_world_example": "Pouring 1/2 cup of apple cider and 1/3 cup of cranberry juice creates 5/6 cup of sparkling punch.",
        "common_mistakes": [
            "Adding the numerators together and denominators together (1/2 + 1/3 = 2/5).",
            "Changing denominators without multiplying the numerators by the same factor.",
            "Subtracting the smaller numerator from the larger regardless of order in mixed numbers."
        ]
    },
    "g5-fractions-multiply": {
        "title": "Multiplying Fractions and Whole Numbers",
        "big_idea": "Multiplying a whole number by a fraction means finding a fractional part of that whole group.",
        "explanation": "To multiply a whole number by a fraction, multiply the whole number by the numerator and keep the denominator. You can write the whole number over 1 and multiply numerators together and denominators together.",
        "worked_example": [
            {"step": 1, "text": "Multiply 4 by 2/3 as repeated parts", "math": "4 * 2/3"},
            {"step": 2, "text": "Multiply whole number 4 by numerator 2", "math": "4 * 2 = 8"},
            {"step": 3, "text": "Write over denominator 3", "math": "4 * 2/3 = 8/3"}
        ],
        "key_vocab": ["Factor", "Product", "Numerator", "Denominator", "Improper Fraction"],
        "real_world_example": "If 4 scholars each drink 2/3 pint of elixir, they drink 8/3 pints in total.",
        "common_mistakes": [
            "Multiplying both numerator and denominator by the whole number.",
            "Believing multiplication always results in a larger number.",
            "Cross-multiplying instead of multiplying straight across."
        ]
    },
    "g5-fractions-divide-unit": {
        "title": "Dividing with Unit Fractions",
        "big_idea": "Dividing by a unit fraction determines how many equal unit-sized pieces fit into a quantity.",
        "explanation": "When dividing a whole number by 1/4, you are finding how many fourths fit inside. Since each whole has 4 fourths, 3 divided by 1/4 equals 3 * 4 = 12. When dividing a unit fraction by a whole number, the piece gets partitioned into even smaller pieces.",
        "worked_example": [
            {"step": 1, "text": "Divide 3 whole loaves into 1/4 loaf portions", "math": "3 // (1/4) = 12"},
            {"step": 2, "text": "Verify by multiplication", "math": "12 * 1/4 = 3"},
            {"step": 3, "text": "Check division of 1/4 into 2 parts", "math": "(1/4) / 2 = 1/8"}
        ],
        "key_vocab": ["Unit Fraction", "Dividend", "Divisor", "Quotient", "Partition"],
        "real_world_example": "Cutting 3 foot-long submarine sandwiches into 1/4 foot servings yields 12 servings.",
        "common_mistakes": [
            "Confusing the order of division (calculating whole / fraction instead of fraction / whole).",
            "Multiplying straight without flipping or reasoning about piece sizes.",
            "Treating the fractional answer as a remainder."
        ]
    },
    "g5-volume": {
        "title": "Volume of Rectangular Prisms",
        "big_idea": "Volume measures 3D space by counting unit cubes packed without gaps or overlaps.",
        "explanation": "The volume of a right rectangular prism is calculated by multiplying its three dimensions: length * width * height. The base area (length * width) tells how many cubes sit on the bottom layer, and height tells how many layers are stacked.",
        "worked_example": [
            {"step": 1, "text": "Find base area for 4 cm length and 3 cm width", "math": "4 * 3 = 12"},
            {"step": 2, "text": "Multiply base area by height of 5 cm", "math": "12 * 5 = 60"},
            {"step": 3, "text": "Confirm formula V = l * w * h", "math": "volume_box(4, 3, 5) = 60"}
        ],
        "key_vocab": ["Volume", "Cubic Units", "Length", "Width", "Height"],
        "real_world_example": "A treasure chest 4 feet long, 3 feet wide, and 5 feet high holds 60 cubic feet of pirate gold.",
        "common_mistakes": [
            "Adding dimensions together (4 + 3 + 5 = 12) instead of multiplying.",
            "Confusing surface area with volume by counting only outside faces.",
            "Forgetting to multiply the base layer by the height."
        ]
    },
    "g5-multiply": {
        "title": "Multi-Digit Multiplication",
        "big_idea": "Multi-digit multiplication breaks numbers into place-value partial products and combines them.",
        "explanation": "To multiply two-digit or three-digit numbers, multiply each digit of the top number by the ones digit of the bottom number, then by the tens digit (placing a 0 placeholder in the ones column), and add the results.",
        "worked_example": [
            {"step": 1, "text": "Multiply 24 by ones digit 3", "math": "24 * 3 = 72"},
            {"step": 2, "text": "Multiply 24 by tens digit 10", "math": "24 * 10 = 240"},
            {"step": 3, "text": "Add the partial products", "math": "72 + 240 = 312"}
        ],
        "key_vocab": ["Partial Product", "Regrouping", "Tens Place", "Factor", "Standard Algorithm"],
        "real_world_example": "An auditorium with 24 rows of 13 seats has 312 total seats.",
        "common_mistakes": [
            "Forgetting to put a zero in the ones place when multiplying by the tens digit.",
            "Multiplying carried numbers instead of adding them.",
            "Misaligning columns when adding partial products."
        ]
    },
    "g5-divide": {
        "title": "Multi-Digit Division with Remainders",
        "big_idea": "Division shares a total into equal groups; any leftover amount that cannot form a full group is the remainder.",
        "explanation": "When dividing whole numbers using long division, divide, multiply, subtract, and bring down. If the final number remaining is smaller than the divisor, record it as remainder R.",
        "worked_example": [
            {"step": 1, "text": "Divide 85 by 4 to find quotient", "math": "85 // 4 = 21"},
            {"step": 2, "text": "Multiply quotient by divisor", "math": "21 * 4 = 84"},
            {"step": 3, "text": "Subtract to find remainder", "math": "85 - 84 = 1"}
        ],
        "key_vocab": ["Dividend", "Divisor", "Quotient", "Remainder", "Long Division"],
        "real_world_example": "Packing 85 apples into boxes of 4 leaves 21 full boxes and 1 leftover apple.",
        "common_mistakes": [
            "Leaving a remainder that is larger than or equal to the divisor.",
            "Making mistakes during intermediate subtraction steps.",
            "Misplacing the quotient digits above the wrong place-value column."
        ]
    },
    "g5-order-ops": {
        "title": "Order of Operations & Expressions",
        "big_idea": "Mathematical expressions follow a standard agreed-upon hierarchy to guarantee one unique value.",
        "explanation": "Follow PEMDAS / Order of Operations: evaluate inside Parentheses first, then Exponents, then Multiplication and Division from left to right, and finally Addition and Subtraction from left to right.",
        "worked_example": [
            {"step": 1, "text": "Evaluate parentheses in 3 + 4 * (5 - 2)", "math": "5 - 2 = 3"},
            {"step": 2, "text": "Perform multiplication before addition", "math": "4 * 3 = 12"},
            {"step": 3, "text": "Add the remaining values", "math": "3 + 12 = 15"}
        ],
        "key_vocab": ["Order of Operations", "Parentheses", "Precedence", "Expression", "Evaluate"],
        "real_world_example": "Buying 3 passes and 4 combo meals with a $2 coupon per meal follows 3 + 4 * (5 - 2) = $15.",
        "common_mistakes": [
            "Calculating strictly from left to right regardless of multiplication.",
            "Always adding before subtracting rather than working left to right.",
            "Ignoring grouping symbols like parentheses."
        ]
    },
    "g6-ratios": {
        "title": "Understanding Ratios & Equivalent Ratios",
        "big_idea": "A ratio is a multiplicative comparison between two quantities.",
        "explanation": "Ratios compare parts to parts or parts to wholes. Equivalent ratios are formed by multiplying or dividing both terms by the exact same non-zero number, just like equivalent fractions.",
        "worked_example": [
            {"step": 1, "text": "Start with ratio of 2 blue to 3 yellow paint drops", "math": "2/3 = 2/3"},
            {"step": 2, "text": "Scale both terms by 4 to make a larger batch", "math": "2 * 4 = 8"},
            {"step": 3, "text": "Scale the second term by 4 and simplify", "math": "3 * 4 = 12"}
        ],
        "key_vocab": ["Ratio", "Equivalent Ratio", "Part-to-Part", "Part-to-Whole", "Scaling"],
        "real_world_example": "Mixing 2 cups of lemon juice with 3 cups of water scales up to 8 cups of lemon juice and 12 cups of water.",
        "common_mistakes": [
            "Adding a constant number to both sides instead of multiplying (e.g. 2:3 -> 3:4).",
            "Confusing part-to-part ratios with part-to-whole ratios.",
            "Reversing the order of terms requested in the problem."
        ]
    },
    "g6-unit-rates": {
        "title": "Unit Rates & Unit Pricing",
        "big_idea": "A unit rate compares a quantity to one single unit of another quantity.",
        "explanation": "To find a unit rate, divide the first quantity by the second quantity so the denominator becomes 1. Common unit rates include miles per hour, dollars per pound, and words per minute.",
        "worked_example": [
            {"step": 1, "text": "Start with $18 for 3 books", "math": "18 / 3 = 6"},
            {"step": 2, "text": "Confirm unit cost per book", "math": "unit_rate(18, 3) = 6"},
            {"step": 3, "text": "Check cost for 5 books at unit rate", "math": "6 * 5 = 30"}
        ],
        "key_vocab": ["Rate", "Unit Rate", "Unit Price", "Per", "Denominator of One"],
        "real_world_example": "Traveling 150 miles in 3 hours means traveling at a unit rate of 50 miles per hour.",
        "common_mistakes": [
            "Dividing in reverse order (dividing hours by miles instead of miles by hours).",
            "Forgetting that the unit rate must express a comparison to exactly 1 unit.",
            "Confusing the units when interpreting speed or unit prices."
        ]
    },
    "g6-percents": {
        "title": "Percents as Rates per 100",
        "big_idea": "A percent represents a ratio comparison of a number out of 100 equal parts.",
        "explanation": "Percent literally means 'per hundred'. To calculate a percent of a number, convert the percent into a fraction with denominator 100 or a decimal, then multiply by the total quantity.",
        "worked_example": [
            {"step": 1, "text": "Write 25% as fraction 25/100 or 1/4", "math": "25/100 = 1/4"},
            {"step": 2, "text": "Multiply 1/4 by 80", "math": "80 / 4 = 20"},
            {"step": 3, "text": "Confirm percent_of formula", "math": "percent_of(25, 80) = 20"}
        ],
        "key_vocab": ["Percent", "Rate per 100", "Decimal Equivalent", "Base", "Portion"],
        "real_world_example": "A 25% discount on an $80 shield saves you $20.",
        "common_mistakes": [
            "Shifting the decimal point the wrong way (e.g. writing 5% as 0.5 instead of 0.05).",
            "Multiplying directly by the percent number without dividing by 100.",
            "Confusing the discount amount with the final sale price."
        ]
    },
    "g6-fraction-division": {
        "title": "Dividing Fractions by Fractions",
        "big_idea": "Dividing by a fraction is equivalent to multiplying by its reciprocal.",
        "explanation": "To divide two fractions, keep the first fraction (the dividend), change the division sign to multiplication, and flip the second fraction (the divisor) to its reciprocal.",
        "worked_example": [
            {"step": 1, "text": "Setup division (3/4) / (1/2)", "math": "(3/4) / (1/2)"},
            {"step": 2, "text": "Multiply by reciprocal of 1/2 which is 2/1", "math": "(3/4) * (2/1) = 6/4"},
            {"step": 3, "text": "Simplify 6/4 to lowest terms", "math": "6/4 = 3/2"}
        ],
        "key_vocab": ["Reciprocal", "Dividend", "Divisor", "Quotient", "Invert"],
        "real_world_example": "If a craft recipe uses 1/2 yard of felt, 3/4 yard of felt provides 3/2 (or 1.5) batches.",
        "common_mistakes": [
            "Inverting the first fraction instead of the second fraction.",
            "Dividing numerators and denominators straight across without common denominators.",
            "Flipping both fractions before multiplying."
        ]
    },
    "g6-decimals": {
        "title": "Multi-Digit Decimal Operations",
        "big_idea": "Decimal operations extend whole-number algorithms while preserving place-value relationships.",
        "explanation": "In multi-digit decimal multiplication, count the total number of decimal digits in both factors to place the decimal in the product. In decimal division, shift the decimal in both divisor and dividend until the divisor is a whole number.",
        "worked_example": [
            {"step": 1, "text": "Multiply 2.5 by 0.4 ignoring decimals first (25 * 4 = 100)", "math": "25 * 4 = 100"},
            {"step": 2, "text": "Place decimal 2 places from right", "math": "2.5 * 0.4 = 1"},
            {"step": 3, "text": "Check with division", "math": "1 / 0.4 = 2.5"}
        ],
        "key_vocab": ["Factor", "Product", "Divisor", "Dividend", "Place Value"],
        "real_world_example": "Buying 2.5 pounds of enchanted seeds at $0.40 per pound costs $1.00.",
        "common_mistakes": [
            "Miscounting total decimal places in the product.",
            "Failing to shift the dividend's decimal when shifting the divisor.",
            "Dropping leading zeros after the decimal point (e.g. writing 0.6 instead of 0.06)."
        ]
    },
    "g6-integers": {
        "title": "Integers and Number Line Opposites",
        "big_idea": "Integers include whole numbers, their negative opposites, and zero on a continuous number line.",
        "explanation": "Positive integers lie to the right of zero on a horizontal number line; negative integers lie to the left. The farther to the left a number lies, the smaller its value: -8 is less than -3.",
        "worked_example": [
            {"step": 1, "text": "Compare -5 and 2", "math": "compare(-5, 2)"},
            {"step": 2, "text": "Compare -8 and -3", "math": "compare(-8, -3)"},
            {"step": 3, "text": "Identify opposite of -5", "math": "abs(-5) = 5"}
        ],
        "key_vocab": ["Integer", "Negative Number", "Positive Number", "Opposite", "Number Line"],
        "real_world_example": "A temperature of -8°F is colder (lower) than -3°F.",
        "common_mistakes": [
            "Believing -8 is greater than -3 because 8 is greater than 3.",
            "Confusing absolute value with opposite sign.",
            "Placing negative numbers in reverse order on the number line."
        ]
    },
    "g6-equiv-expressions": {
        "title": "Generating Equivalent Algebraic Expressions",
        "big_idea": "Applying algebraic properties produces equivalent expressions that equal the same value for any substitution.",
        "explanation": "Use the Distributive Property: a(b + c) = ab + ac. Combine like terms by adding their numerical coefficients, such as 3x + 5x = 8x.",
        "worked_example": [
            {"step": 1, "text": "Distribute 3 across (2x + 4)", "math": "3 * 2 = 6"},
            {"step": 2, "text": "Distribute 3 to constant term 4", "math": "3 * 4 = 12"},
            {"step": 3, "text": "Combine terms to form expression", "math": "3 * 4 + 6 = 18"}
        ],
        "key_vocab": ["Distributive Property", "Coefficient", "Like Terms", "Equivalent Expression", "Variable"],
        "real_world_example": "Buying 3 packs containing x notebooks and 4 pens yields 3x notebooks and 12 pens.",
        "common_mistakes": [
            "Multiplying the outside factor by the first term only (e.g. 3(x + 4) = 3x + 4).",
            "Adding variable terms and constant terms together (e.g. 4x + 5 = 9x).",
            "Making sign errors when distributing a negative coefficient."
        ]
    },
    "g6-equations": {
        "title": "Solving One-Step Equations",
        "big_idea": "An equation is a balanced scale; perform inverse operations on both sides to solve for the unknown variable.",
        "explanation": "To isolate the variable, perform the opposite (inverse) operation on both sides of the equal sign. Undo addition with subtraction, subtraction with addition, multiplication with division, and division with multiplication.",
        "worked_example": [
            {"step": 1, "text": "Solve x + 7 = 19 by subtracting 7 from both sides", "math": "19 - 7 = 12"},
            {"step": 2, "text": "Check solution in equation", "math": "12 + 7 = 19"},
            {"step": 3, "text": "Solve 3x = 18 by dividing by 3", "math": "18 / 3 = 6"}
        ],
        "key_vocab": ["Equation", "Variable", "Inverse Operation", "Isolate", "Solution"],
        "real_world_example": "If a mystery pouch plus 7 gold coins weighs 19 coins, the pouch holds 12 coins.",
        "common_mistakes": [
            "Adding when the equation already has addition instead of subtracting.",
            "Performing the inverse operation on one side without balancing the other side.",
            "Multiplying coefficients instead of dividing."
        ]
    },
    "g6-mean-median": {
        "title": "Measures of Center: Mean & Median",
        "big_idea": "Mean and median summarize a whole set of data points into a single central representative value.",
        "explanation": "The mean (equal share value) is found by adding all data points and dividing by the total number of points. The median is the physical middle value when data is arranged in numerical order from least to greatest.",
        "worked_example": [
            {"step": 1, "text": "Find sum of scores 10, 20, 30, 40", "math": "10 + 20 + 30 + 40 = 100"},
            {"step": 2, "text": "Divide sum by count of 4", "math": "100 / 4 = 25"},
            {"step": 3, "text": "Verify with mean function", "math": "mean(10, 20, 30, 40) = 25"}
        ],
        "key_vocab": ["Mean", "Median", "Center", "Data Set", "Equal Share"],
        "real_world_example": "If 4 friends catch 10, 20, 30, and 40 fish, sharing them equally gives a mean of 25 fish each.",
        "common_mistakes": [
            "Picking the middle number before sorting the data in numerical order.",
            "Dividing the sum by 2 instead of the number of data points.",
            "Confusing mean (average) with median (middle value)."
        ]
    },
    "g6-exponents": {
        "title": "Numerical Expressions with Exponents",
        "big_idea": "Exponents represent repeated multiplication of the same base number.",
        "explanation": "In the exponential expression 2^3, 2 is the base and 3 is the exponent. The exponent tells how many times to multiply the base by itself: 2 * 2 * 2 = 8, not 2 * 3 = 6.",
        "worked_example": [
            {"step": 1, "text": "Evaluate 2 squared (2^2)", "math": "2 * 2 = 4"},
            {"step": 2, "text": "Evaluate 2 cubed (2^3)", "math": "4 * 2 = 8"},
            {"step": 3, "text": "Verify power 2^4", "math": "2 ** 4 = 16"}
        ],
        "key_vocab": ["Base", "Exponent", "Power", "Squared", "Cubed"],
        "real_world_example": "A magical crystal that doubles every hour starts at 1, then reaches 2^3 = 8 crystals in 3 hours.",
        "common_mistakes": [
            "Multiplying the base by the exponent (e.g. thinking 2^3 = 6 instead of 8).",
            "Believing any base to the power of 0 equals 0 instead of 1.",
            "Switching the base and exponent."
        ]
    }
}


FLAGSHIP_INFOGRAPHICS = {
    "g5-fractions-add": {
        "title": "The Four Alchemical Steps of Fraction Addition",
        "steps": [
            {"label": "Inspect Denominators", "detail": "Check if denominators are the same.", "math": "1/4 + 1/2"},
            {"label": "Find Common Multiple", "detail": "Choose least common denominator (4).", "math": "2 * 2 = 4"},
            {"label": "Rename Fractions", "detail": "Multiply numerator and denominator equally.", "math": "1/2 = 2/4"},
            {"label": "Combine Numerators", "detail": "Add top numbers while keeping bottom.", "math": "1/4 + 2/4 = 3/4"}
        ],
        "example": "1/4 + 1/2 = 1/4 + 2/4 = 3/4",
        "image_prompt": "An illuminated medieval alchemy bench with glowing crystalline fraction flasks combining blue and gold elixirs into a luminous chalice."
    },
    "g6-ratios": {
        "title": "The Harmonic Scale of Equivalent Ratios",
        "steps": [
            {"label": "Identify Terms", "detail": "Write the initial relationship.", "math": "2:3"},
            {"label": "Choose Multiplier", "detail": "Select constant scaling factor (3).", "math": "3 = 3"},
            {"label": "Scale First Term", "detail": "Multiply the first term.", "math": "2 * 3 = 6"},
            {"label": "Scale Second Term", "detail": "Multiply second term by same factor.", "math": "3 * 3 = 9"}
        ],
        "example": "2:3 scales up to 6:9",
        "image_prompt": "A fantasy botanical greenhouse with glowing runic vines branching into balanced crystal pedestals holding emerald berries."
    },
    "g5-volume": {
        "title": "Layering the Cubic Monolith",
        "steps": [
            {"label": "Measure Length", "detail": "Count front unit cubes.", "math": "4 = 4"},
            {"label": "Measure Width", "detail": "Count depth unit cubes.", "math": "3 = 3"},
            {"label": "Calculate Base Area", "detail": "Multiply length by width.", "math": "4 * 3 = 12"},
            {"label": "Multiply by Height", "detail": "Multiply base layer by vertical stack (5).", "math": "12 * 5 = 60"}
        ],
        "example": "4 cm * 3 cm * 5 cm = 60 cm³",
        "image_prompt": "An obsidian temple chamber featuring a translucent floating rectangular prism composed of glowing sapphire unit cubes."
    }
}


FLAGSHIP_EXPLAINERS = {
    "g5-fractions-add": {
        "slides": [
            {
                "title": "The Denominator Riddle",
                "visual_hint": "Two ancient tablets showing 1/4 and 1/2.",
                "narration": "Welcome, young scholar. Fractions are parts of a whole, but they can only unite when their slices are the same size.",
                "highlight": "slices"
            },
            {
                "title": "Different Sizes Cannot Blend",
                "visual_hint": "A large half-shield next to a small quarter-shield.",
                "narration": "Notice the denominators: four and two. We cannot simply add one plus one to get two-sixths. That is an ancient trap!",
                "highlight": "two-sixths"
            },
            {
                "title": "Summon the Common Denominator",
                "visual_hint": "The half-shield dividing down the center into two quarters.",
                "narration": "We can transform one-half into two-fourths. Now both fractions share the exact same denominator.",
                "highlight": "two-fourths"
            },
            {
                "title": "Unite the Numerators",
                "visual_hint": "One quarter-flask and two quarter-flasks pouring into a bowl.",
                "narration": "Add the numerators: one plus two equals three. The denominator stays four.",
                "highlight": "three-fourths"
            },
            {
                "title": "The Master Formula",
                "visual_hint": "A glowing stone formula: 1/4 + 2/4 = 3/4.",
                "narration": "One-fourth plus one-half equals three-fourths. You have mastered fraction addition!",
                "highlight": "mastered"
            },
            {
                "title": "Scholar Victory",
                "visual_hint": "A golden scholar badge shining on the screen.",
                "narration": "Remember: always equalize denominators before adding the numerators. Onward to your next quest!",
                "highlight": "equalize"
            }
        ]
    },
    "g6-ratios": {
        "slides": [
            {
                "title": "The Merchant's Scale",
                "visual_hint": "A balance scale with 2 blue gems on the left and 3 amber gems on the right.",
                "narration": "A ratio is a relationship comparing two amounts. Here, for every two blue gems, we need three amber gems.",
                "highlight": "two to three"
            },
            {
                "title": "Scaling the Magic",
                "visual_hint": "Two pouches appearing beside each pile.",
                "narration": "What if we need a larger batch? We must scale both amounts by the same multiplier.",
                "highlight": "multiplier"
            },
            {
                "title": "Avoid the Addition Trap",
                "visual_hint": "A warning rune glowing red over a '+1' icon.",
                "narration": "Never add a number to both sides. Ratios scale by multiplication, not addition!",
                "highlight": "multiplication"
            },
            {
                "title": "Multiplying in Harmony",
                "visual_hint": "2 times 3 becomes 6 gems; 3 times 3 becomes 9 gems.",
                "narration": "Multiplying both sides by three yields six blue gems to nine amber gems. The balance holds!",
                "highlight": "six to nine"
            },
            {
                "title": "Simplifying Back",
                "visual_hint": "Dividing 6 and 9 by 3 to return to 2:3.",
                "narration": "Dividing both terms by their common factor brings us right back to simplest form: two to three.",
                "highlight": "simplest form"
            },
            {
                "title": "Proportion Mastery",
                "visual_hint": "A glowing heraldic crest of the merchant guild.",
                "narration": "Keep your ratios balanced and your trades will always be true. Well done, scholar!",
                "highlight": "balanced"
            }
        ]
    },
    "g5-volume": {
        "slides": [
            {
                "title": "Entering the Third Dimension",
                "visual_hint": "A flat 2D blueprint rising into a 3D glass box.",
                "narration": "Area covers a flat floor, but volume fills an entire room. We measure volume using unit cubes.",
                "highlight": "unit cubes"
            },
            {
                "title": "The Floor Layer",
                "visual_hint": "A grid of 4 cubes long by 3 cubes wide.",
                "narration": "Look at the base. A length of four and a width of three creates a floor of twelve cubes.",
                "highlight": "twelve cubes"
            },
            {
                "title": "Stacking the Height",
                "visual_hint": "Five layers of twelve cubes stacking vertically.",
                "narration": "Now stack that base five layers high. Each layer holds twelve cubes.",
                "highlight": "five layers"
            },
            {
                "title": "The Volume Equation",
                "visual_hint": "Length times Width times Height = 4 * 3 * 5 = 60.",
                "narration": "Multiply length times width times height. Four times three times five equals sixty cubic units.",
                "highlight": "sixty cubic units"
            },
            {
                "title": "No Gaps, No Overlaps",
                "visual_hint": "The box sealing tight with solid blue glowing cubes.",
                "narration": "Every single cube fits perfectly inside with no gaps and no overlaps.",
                "highlight": "no gaps"
            },
            {
                "title": "Master of Dimensions",
                "visual_hint": "A glowing isometric prism badge.",
                "narration": "You now understand volume from the foundation to the ceiling. Great questing!",
                "highlight": "foundation"
            }
        ]
    }
}


def build_all_lessons_and_bundles():
    os.makedirs("data/lessons", exist_ok=True)
    os.makedirs("data/infographics", exist_ok=True)
    os.makedirs("data/explainers", exist_ok=True)

    print("Authoring and verifying lessons for all 20 Georgia Math Standards topics...")
    for tid, l_dict in ALL_LESSONS.items():
        lesson_obj = Lesson(
            title=l_dict["title"],
            big_idea=l_dict["big_idea"],
            explanation=l_dict["explanation"],
            worked_example=[WorkedStep(**step) for step in l_dict["worked_example"]],
            key_vocab=l_dict["key_vocab"],
            real_world_example=l_dict["real_world_example"],
            common_mistakes=l_dict["common_mistakes"]
        )

        res = verify_lesson(lesson_obj)
        if not res.passed:
            raise ValueError(f"Lesson verification failed for {tid}: {res.reasons}")

        data_to_write = lesson_obj.model_dump()
        data_to_write["source"] = "hand-authored"
        data_to_write["topic_id"] = tid

        out_path = os.path.join("data/lessons", f"{tid}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data_to_write, f, indent=2)

    print(f"Successfully verified and saved {len(ALL_LESSONS)} lessons.")

    # Flagship Infographics
    print("Authoring flagship infographics...")
    for tid, info_dict in FLAGSHIP_INFOGRAPHICS.items():
        info_obj = InfographicData(
            title=info_dict["title"],
            steps=[InfographicStep(**s) for s in info_dict["steps"]],
            example=info_dict["example"],
            image_prompt=info_dict["image_prompt"]
        )
        out_path = os.path.join("data/infographics", f"{tid}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(info_obj.model_dump(), f, indent=2)

    # Flagship Explainers
    print("Authoring flagship explainer scripts...")
    for tid, exp_dict in FLAGSHIP_EXPLAINERS.items():
        exp_obj = ExplainerScript(
            slides=[Slide(**s) for s in exp_dict["slides"]]
        )
        out_path = os.path.join("data/explainers", f"{tid}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(exp_obj.model_dump(), f, indent=2)

    print("Flagship content authoring complete.")


if __name__ == "__main__":
    build_all_lessons_and_bundles()
