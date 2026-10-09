"""
PowerCalc - Advanced Python Calculator
=======================================
A feature-rich, extensible calculator supporting arithmetic, scientific,
statistical, matrix, and financial operations.

Author: PowerCalc
Version: 2.0.0
License: MIT
"""

import math
import statistics
import cmath
from typing import Union, List, Tuple
from functools import reduce
import operator

Number = Union[int, float, complex]


# ─────────────────────────────────────────────────────────────────────────────
# BASE CLASS
# ─────────────────────────────────────────────────────────────────────────────

class Calculator:
    """
    Base calculator providing core arithmetic operations.

    Attributes:
        history (list): List of past calculations as (expression, result) tuples.
        memory (float): Stored memory value.
        precision (int): Decimal places for rounding results.

    Example:
        >>> calc = Calculator()
        >>> calc.add(3, 5)
        8
        >>> calc.divide(10, 3)
        3.3333333333333335
    """

    def __init__(self, precision: int = 10):
        self.history: List[Tuple[str, Number]] = []
        self.memory: float = 0.0
        self.precision = precision

    def _record(self, expression: str, result: Number) -> Number:
        self.history.append((expression, result))
        return result

    def add(self, a: Number, b: Number) -> Number:
        """Return the sum of a and b."""
        return self._record(f"{a} + {b}", a + b)

    def subtract(self, a: Number, b: Number) -> Number:
        """Return the difference of a and b."""
        return self._record(f"{a} - {b}", a - b)

    def multiply(self, a: Number, b: Number) -> Number:
        """Return the product of a and b."""
        return self._record(f"{a} × {b}", a * b)

    def divide(self, a: Number, b: Number) -> Number:
        """Return the quotient of a divided by b. Raises ZeroDivisionError if b == 0."""
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero.")
        return self._record(f"{a} ÷ {b}", a / b)

    def floor_divide(self, a: Number, b: Number) -> Number:
        """Return the integer (floor) quotient of a divided by b."""
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero.")
        return self._record(f"{a} // {b}", a // b)

    def modulo(self, a: Number, b: Number) -> Number:
        """Return the remainder of a divided by b."""
        if b == 0:
            raise ZeroDivisionError("Cannot mod by zero.")
        return self._record(f"{a} % {b}", a % b)

    def power(self, base: Number, exp: Number) -> Number:
        """Return base raised to the power of exp."""
        return self._record(f"{base} ^ {exp}", base ** exp)

    def absolute(self, a: Number) -> Number:
        """Return the absolute value of a."""
        return self._record(f"|{a}|", abs(a))

    def negate(self, a: Number) -> Number:
        """Return the negation of a."""
        return self._record(f"-({a})", -a)

    # ── Memory ──────────────────────────────────────────────────────────────

    def memory_store(self, value: float) -> None:
        """Store value in memory."""
        self.memory = value

    def memory_recall(self) -> float:
        """Recall the stored memory value."""
        return self.memory

    def memory_clear(self) -> None:
        """Clear memory to 0."""
        self.memory = 0.0

    def memory_add(self, value: float) -> None:
        """Add value to memory."""
        self.memory += value

    # ── History ─────────────────────────────────────────────────────────────

    def clear_history(self) -> None:
        """Clear all calculation history."""
        self.history.clear()

    def show_history(self) -> List[str]:
        """Return history as formatted strings."""
        return [f"{expr} = {result}" for expr, result in self.history]


# ─────────────────────────────────────────────────────────────────────────────
# SCIENTIFIC CALCULATOR
# ─────────────────────────────────────────────────────────────────────────────

class ScientificCalculator(Calculator):
    """
    Extends Calculator with trigonometric, logarithmic, and advanced math.
    """

    def sin(self, angle_rad: float) -> float:
        return self._record(f"sin({angle_rad})", math.sin(angle_rad))

    def cos(self, angle_rad: float) -> float:
        return self._record(f"cos({angle_rad})", math.cos(angle_rad))

    def tan(self, angle_rad: float) -> float:
        return self._record(f"tan({angle_rad})", math.tan(angle_rad))

    def asin(self, x: float) -> float:
        return self._record(f"asin({x})", math.asin(x))

    def acos(self, x: float) -> float:
        return self._record(f"acos({x})", math.acos(x))

    def atan(self, x: float) -> float:
        return self._record(f"atan({x})", math.atan(x))

    def atan2(self, y: float, x: float) -> float:
        return self._record(f"atan2({y},{x})", math.atan2(y, x))

    def degrees(self, rad: float) -> float:
        return self._record(f"deg({rad})", math.degrees(rad))

    def radians(self, deg: float) -> float:
        return self._record(f"rad({deg})", math.radians(deg))

    def sinh(self, x: float) -> float:
        return self._record(f"sinh({x})", math.sinh(x))

    def cosh(self, x: float) -> float:
        return self._record(f"cosh({x})", math.cosh(x))

    def tanh(self, x: float) -> float:
        return self._record(f"tanh({x})", math.tanh(x))

    def log(self, x: float, base: float = math.e) -> float:
        if x <= 0:
            raise ValueError("Logarithm undefined for non-positive values.")
        return self._record(f"log_{base}({x})", math.log(x, base))

    def log10(self, x: float) -> float:
        if x <= 0:
            raise ValueError("Logarithm undefined for non-positive values.")
        return self._record(f"log10({x})", math.log10(x))

    def log2(self, x: float) -> float:
        if x <= 0:
            raise ValueError("Logarithm undefined for non-positive values.")
        return self._record(f"log2({x})", math.log2(x))

    def exp(self, x: float) -> float:
        return self._record(f"e^{x}", math.exp(x))

    def sqrt(self, x: float) -> float:
        if x < 0:
            raise ValueError("Square root of negative number. Use complex_sqrt.")
        return self._record(f"sqrt({x})", math.sqrt(x))

    def cbrt(self, x: float) -> float:
        result = math.copysign(abs(x) ** (1 / 3), x)
        return self._record(f"cbrt({x})", result)

    def nth_root(self, x: float, n: float) -> float:
        return self._record(f"{n}root({x})", x ** (1 / n))

    def complex_sqrt(self, x: complex) -> complex:
        return self._record(f"csqrt({x})", cmath.sqrt(x))

    def factorial(self, n: int) -> int:
        if not isinstance(n, int) or n < 0:
            raise ValueError("Factorial defined only for non-negative integers.")
        return self._record(f"{n}!", math.factorial(n))

    def permutation(self, n: int, r: int) -> int:
        if r > n:
            raise ValueError("r cannot be greater than n.")
        return self._record(f"P({n},{r})", math.factorial(n) // math.factorial(n - r))

    def combination(self, n: int, r: int) -> int:
        return self._record(f"C({n},{r})", math.comb(n, r))

    @property
    def PI(self) -> float:
        return math.pi

    @property
    def E(self) -> float:
        return math.e

    @property
    def TAU(self) -> float:
        return math.tau

    @property
    def PHI(self) -> float:
        return (1 + math.sqrt(5)) / 2


# ─────────────────────────────────────────────────────────────────────────────
# STATISTICAL CALCULATOR
# ─────────────────────────────────────────────────────────────────────────────

class StatisticalCalculator(ScientificCalculator):

    def mean(self, data: List[float]) -> float:
        return self._record(f"mean({data})", statistics.mean(data))

    def median(self, data: List[float]) -> float:
        return self._record(f"median({data})", statistics.median(data))

    def mode(self, data: List[float]) -> float:
        return self._record(f"mode({data})", statistics.mode(data))

    def std_dev(self, data: List[float], population: bool = False) -> float:
        fn = statistics.pstdev if population else statistics.stdev
        label = "sigma" if population else "s"
        return self._record(f"{label}({data})", fn(data))

    def variance(self, data: List[float], population: bool = False) -> float:
        fn = statistics.pvariance if population else statistics.variance
        return self._record(f"var({data})", fn(data))

    def data_range(self, data: List[float]) -> float:
        return self._record(f"range({data})", max(data) - min(data))

    def percentile(self, data: List[float], p: float) -> float:
        sorted_data = sorted(data)
        k = (len(sorted_data) - 1) * (p / 100)
        f, c = math.floor(k), math.ceil(k)
        result = sorted_data[f] if f == c else sorted_data[f] * (c - k) + sorted_data[c] * (k - f)
        return self._record(f"P{p}({data})", result)

    def correlation(self, x: List[float], y: List[float]) -> float:
        n = len(x)
        if n != len(y):
            raise ValueError("Datasets must be of equal length.")
        mx, my = statistics.mean(x), statistics.mean(y)
        num = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
        den = math.sqrt(
            sum((xi - mx) ** 2 for xi in x) * sum((yi - my) ** 2 for yi in y)
        )
        if den == 0:
            raise ValueError("Correlation undefined: zero variance.")
        return self._record(f"corr(x,y)", num / den)

    def sum_data(self, data: List[float]) -> float:
        return self._record(f"sum({data})", sum(data))

    def product_data(self, data: List[float]) -> float:
        return self._record(f"product({data})", reduce(operator.mul, data, 1))

    def geometric_mean(self, data: List[float]) -> float:
        if any(x <= 0 for x in data):
            raise ValueError("Geometric mean requires all positive values.")
        return self._record(f"geo_mean({data})", statistics.geometric_mean(data))

    def harmonic_mean(self, data: List[float]) -> float:
        return self._record(f"harm_mean({data})", statistics.harmonic_mean(data))


# ─────────────────────────────────────────────────────────────────────────────
# FINANCIAL CALCULATOR
# ─────────────────────────────────────────────────────────────────────────────

class FinancialCalculator(StatisticalCalculator):

    def simple_interest(self, principal: float, rate: float, time: float) -> float:
        return self._record(f"SI({principal},{rate},{time})", principal * rate * time)

    def compound_interest(self, principal: float, rate: float, n: int, t: float) -> float:
        result = principal * (1 + rate / n) ** (n * t)
        return self._record(f"CI({principal},{rate},{n},{t})", result)

    def present_value(self, future_value: float, rate: float, periods: int) -> float:
        return self._record(f"PV({future_value},{rate},{periods})", future_value / (1 + rate) ** periods)

    def future_value(self, present_value: float, rate: float, periods: int) -> float:
        return self._record(f"FV({present_value},{rate},{periods})", present_value * (1 + rate) ** periods)

    def loan_payment(self, principal: float, annual_rate: float, years: int, payments_per_year: int = 12) -> float:
        r = annual_rate / payments_per_year
        n = years * payments_per_year
        if r == 0:
            return principal / n
        result = principal * r * (1 + r) ** n / ((1 + r) ** n - 1)
        return self._record(f"PMT({principal},{annual_rate},{years}y)", result)

    def roi(self, gain: float, cost: float) -> float:
        if cost == 0:
            raise ZeroDivisionError("Cost cannot be zero.")
        return self._record(f"ROI({gain},{cost})", ((gain - cost) / cost) * 100)

    def break_even(self, fixed_costs: float, price_per_unit: float, variable_cost_per_unit: float) -> float:
        margin = price_per_unit - variable_cost_per_unit
        if margin <= 0:
            raise ValueError("Price must exceed variable cost.")
        return self._record(f"BEP({fixed_costs},{price_per_unit},{variable_cost_per_unit})", fixed_costs / margin)

    def inflation_adjusted(self, amount: float, inflation_rate: float, years: int) -> float:
        return self._record(f"inflation_adj({amount},{inflation_rate},{years}y)", amount / (1 + inflation_rate) ** years)


# ─────────────────────────────────────────────────────────────────────────────
# MATRIX CALCULATOR
# ─────────────────────────────────────────────────────────────────────────────

Matrix = List[List[float]]


class MatrixCalculator:

    def _validate(self, A: Matrix, B: Matrix = None, op: str = "") -> None:
        if B is not None:
            if len(A) != len(B) or len(A[0]) != len(B[0]):
                raise ValueError(f"Matrix dimensions must match for {op}.")

    def add(self, A: Matrix, B: Matrix) -> Matrix:
        self._validate(A, B, "addition")
        return [[A[i][j] + B[i][j] for j in range(len(A[0]))] for i in range(len(A))]

    def subtract(self, A: Matrix, B: Matrix) -> Matrix:
        self._validate(A, B, "subtraction")
        return [[A[i][j] - B[i][j] for j in range(len(A[0]))] for i in range(len(A))]

    def multiply(self, A: Matrix, B: Matrix) -> Matrix:
        if len(A[0]) != len(B):
            raise ValueError("A's columns must equal B's rows.")
        rows, cols, inner = len(A), len(B[0]), len(B)
        return [[sum(A[i][k] * B[k][j] for k in range(inner)) for j in range(cols)] for i in range(rows)]

    def scalar_multiply(self, A: Matrix, k: float) -> Matrix:
        return [[k * A[i][j] for j in range(len(A[0]))] for i in range(len(A))]

    def transpose(self, A: Matrix) -> Matrix:
        return [[A[j][i] for j in range(len(A))] for i in range(len(A[0]))]

    def determinant(self, A: Matrix) -> float:
        n = len(A)
        if any(len(row) != n for row in A):
            raise ValueError("Matrix must be square.")
        mat = [row[:] for row in A]
        det = 1.0
        for col in range(n):
            pivot = max(range(col, n), key=lambda r: abs(mat[r][col]))
            if mat[pivot][col] == 0:
                return 0.0
            if pivot != col:
                mat[col], mat[pivot] = mat[pivot], mat[col]
                det *= -1
            det *= mat[col][col]
            for row in range(col + 1, n):
                factor = mat[row][col] / mat[col][col]
                for k in range(col, n):
                    mat[row][k] -= factor * mat[col][k]
        return det

    def identity(self, n: int) -> Matrix:
        return [[1 if i == j else 0 for j in range(n)] for i in range(n)]

    def trace(self, A: Matrix) -> float:
        n = min(len(A), len(A[0]))
        return sum(A[i][i] for i in range(n))

    def flatten(self, A: Matrix) -> List[float]:
        return [val for row in A for val in row]


# ─────────────────────────────────────────────────────────────────────────────
# POWERFULLY UNIFIED CALCULATOR
# ─────────────────────────────────────────────────────────────────────────────

class PowerCalc(FinancialCalculator):
    """
    PowerCalc - The unified calculator class.

    ─────────────────────────────────────────────────────────────
    CREATIONAL PATTERN 1 — SINGLETON
    ─────────────────────────────────────────────────────────────
    Only one PowerCalc instance can ever exist in the process.
    Every call to PowerCalc() returns the same object, so history,
    memory, and state are always shared across the entire app.

    Usage:
        a = PowerCalc()
        b = PowerCalc()
        assert a is b          # True — same instance
        a.memory_store(42)
        print(b.memory_recall()) # 42 — same state
    """

    VERSION    = "2.0.0"
    _instance  = None          # class-level slot for the single instance

    def __new__(cls, precision: int = 10):
        """Return the existing instance, or create it on first call."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, precision: int = 10):
        # Guard: only initialise once (subsequent calls are no-ops)
        if getattr(self, "_initialised", False):
            return
        super().__init__(precision=precision)
        self.matrix       = MatrixCalculator()
        self._initialised = True

    def evaluate(self, expression: str) -> Number:
        allowed = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
        allowed.update({"abs": abs, "round": round, "pi": math.pi, "e": math.e})
        try:
            result = eval(expression, {"__builtins__": {}}, allowed)
        except Exception as ex:
            raise ValueError(f"Invalid expression: {ex}")
        return self._record(expression, result)

    def chain(self, start: Number, *operations) -> Number:
        result = start
        for op in operations:
            name, *args = op
            method = getattr(self, name, None)
            if method is None:
                raise AttributeError(f"Unknown operation: {name}")
            result = method(result, *args)
        return result

    def info(self) -> str:
        return (
            f"PowerCalc v{self.VERSION}\n"
            f"Operations in history: {len(self.history)}\n"
            f"Memory: {self.memory}\n"
            f"Capabilities: Arithmetic, Scientific, Statistical, Financial, Matrix"
        )


# ─────────────────────────────────────────────────────────────────────────────
# DEMO / QUICK TEST
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    pc = PowerCalc()

    print("=" * 60)
    print("  PowerCalc Demo")
    print("=" * 60)

    print("\n-- Arithmetic -----------------------------------------")
    print(f"  7 + 3        = {pc.add(7, 3)}")
    print(f"  15 - 8       = {pc.subtract(15, 8)}")
    print(f"  6 x 7        = {pc.multiply(6, 7)}")
    print(f"  22 / 7       = {pc.divide(22, 7):.6f}")
    print(f"  2 ^ 10       = {pc.power(2, 10)}")

    print("\n-- Scientific -----------------------------------------")
    print(f"  sin(pi/2)    = {pc.sin(pc.PI / 2)}")
    print(f"  log10(1000)  = {pc.log10(1000)}")
    print(f"  sqrt(144)    = {pc.sqrt(144)}")
    print(f"  10!          = {pc.factorial(10)}")
    print(f"  C(10,3)      = {pc.combination(10, 3)}")

    print("\n-- Statistical ----------------------------------------")
    data = [4, 7, 13, 2, 1, 9, 8, 6, 5]
    print(f"  data         = {data}")
    print(f"  mean         = {pc.mean(data):.4f}")
    print(f"  median       = {pc.median(data)}")
    print(f"  std dev      = {pc.std_dev(data):.4f}")
    print(f"  P75          = {pc.percentile(data, 75):.4f}")

    print("\n-- Financial ------------------------------------------")
    print(f"  CI $1000 @5% monthly 3y = ${pc.compound_interest(1000, 0.05, 12, 3):.2f}")
    print(f"  Loan PMT $200k @6% 30y  = ${pc.loan_payment(200000, 0.06, 30):.2f}")
    print(f"  ROI: gain=1500 cost=1000 = {pc.roi(1500, 1000):.1f}%")

    print("\n-- Matrix ---------------------------------------------")
    A = [[1, 2], [3, 4]]
    B = [[5, 6], [7, 8]]
    print(f"  det([[1,2],[3,4]]) = {pc.matrix.determinant(A)}")
    print(f"  A x B = {pc.matrix.multiply(A, B)}")

    print("\n-- Expression Evaluator --------------------------------")
    print(f"  '2**8 + sqrt(36)' = {pc.evaluate('2**8 + sqrt(36)')}")

    print("\n-- Chain -----------------------------------------------")
    r = pc.chain(10, ('add', 5), ('multiply', 2), ('sqrt',))
    print(f"  chain(10, +5, x2, sqrt) = {r:.6f}")

    print("\n" + "=" * 60)
    print(pc.info())
    print("=" * 60)
