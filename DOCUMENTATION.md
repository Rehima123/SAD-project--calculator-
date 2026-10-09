# PowerCalc 2.0 — Software Architecture Design Document

> **Project:** PowerCalc 2.0  
> **Type:** Software Architecture Design (SAD) Project  
> **Language:** Python 3.x  
> **GUI Framework:** CustomTkinter  
> **Version:** 2.0.0  
> **Author:** PowerCalc Team  

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Module Structure](#3-module-structure)
4. [Design Patterns](#4-design-patterns)
   - 4.1 Creational — Singleton
   - 4.2 Creational — Factory Method
   - 4.3 Behavioral — Command
   - 4.4 Behavioral — Observer
   - 4.5 Behavioral — Strategy
   - 4.6 Structural — Facade
   - 4.7 Behavioral — Template Method
5. [Class Reference — Engine](#5-class-reference--engine-calculator-py)
6. [Class Reference — GUI](#6-class-reference--gui-calculator_guipy)
7. [Data Flow](#7-data-flow)
8. [Component Interaction Diagram](#8-component-interaction-diagram)
9. [How to Run](#9-how-to-run)

---

## 1. Project Overview

PowerCalc is a full-featured desktop calculator application. It is split into two separate files so that the calculation logic and the user interface are completely independent of each other.

| File | Role |
|---|---|
| `calculator .py` | The calculation engine — pure Python, no UI code |
| `calculator_gui.py` | The graphical interface — CustomTkinter frontend |

The engine can be imported and used on its own in any Python script or test. The GUI simply calls the engine and displays the results.

### Supported Operations

| Category | What it does |
|---|---|
| **Arithmetic** | Add, subtract, multiply, divide, floor divide, modulo, power, absolute value, negate |
| **Scientific** | Trigonometry (sin/cos/tan and inverses), hyperbolic, logarithms, exponentials, roots, factorial, permutations, combinations |
| **Statistical** | Mean, median, mode, standard deviation, variance, range, percentile, correlation, sum, product, geometric mean, harmonic mean |
| **Financial** | Simple/compound interest, present value, future value, loan payment, ROI, break-even point, inflation adjustment |
| **Matrix** | Add, subtract, multiply, scalar multiply, transpose, determinant, trace, identity matrix, flatten |
| **Expression Evaluator** | Type any math expression (e.g. `2**8 + sqrt(36)`) and evaluate it safely |
| **Memory** | MS (store), MR (recall), MC (clear), M+ (add to memory) |
| **History** | Last 50 calculations, viewable in a side panel, clearable |

---

## 2. System Architecture

The project uses a **3-layer architecture**:

```
┌──────────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                           │
│                     calculator_gui.py                            │
│                                                                  │
│   CalculatorApp  ──  5 Tab Views  ──  History Panel             │
│        │                                                         │
│   ┌────▼─────────────────────────────────────────────────────┐  │
│   │              DESIGN PATTERN LAYER                        │  │
│   │  Command  → CalcCommand + CommandHistory  (Undo)         │  │
│   │  Observer → HistorySubject (auto-update display/history) │  │
│   │  Strategy → ThemeContext + ThemeStrategy (themes)        │  │
│   │  Factory  → TabFactory × 5  (tab creation)               │  │
│   └────────────────────────┬─────────────────────────────────┘  │
└────────────────────────────┼─────────────────────────────────────┘
                             │  calls
┌────────────────────────────▼─────────────────────────────────────┐
│                      ENGINE LAYER                                 │
│                      calculator .py                               │
│                                                                   │
│   PowerCalc  (Singleton + Facade)                                 │
│     └── FinancialCalculator                                       │
│           └── StatisticalCalculator                               │
│                 └── ScientificCalculator                          │
│                       └── Calculator  (Template Method)           │
│                                                                   │
│   MatrixCalculator  (composed inside PowerCalc)                   │
└───────────────────────────────────────────────────────────────────┘
```

**Key principle:** The GUI never performs calculations itself. It always delegates to the engine (`PowerCalc`). This makes it easy to test the engine independently and swap the GUI if needed.

---

## 3. Module Structure

### `calculator .py`

```
calculator .py
│
├── Calculator                        ← Base class
│   ├── _record(expr, result)         ← Template Method: logs every result
│   ├── add / subtract / multiply / divide / power / ...
│   └── memory_store / recall / clear / add
│
├── ScientificCalculator(Calculator)
│   ├── sin / cos / tan / asin / acos / atan
│   ├── sinh / cosh / tanh
│   ├── log / log10 / log2 / exp
│   ├── sqrt / cbrt / nth_root
│   └── factorial / permutation / combination
│
├── StatisticalCalculator(ScientificCalculator)
│   ├── mean / median / mode
│   ├── std_dev / variance / data_range
│   ├── percentile / correlation
│   └── sum_data / product_data / geometric_mean / harmonic_mean
│
├── FinancialCalculator(StatisticalCalculator)
│   ├── simple_interest / compound_interest
│   ├── present_value / future_value
│   ├── loan_payment / roi / break_even
│   └── inflation_adjusted
│
├── MatrixCalculator                  ← Standalone, no inheritance
│   ├── add / subtract / multiply / scalar_multiply
│   ├── transpose / determinant
│   └── identity / trace / flatten
│
└── PowerCalc(FinancialCalculator)    ← SINGLETON + FACADE
    ├── __new__()                     ← Enforces single instance
    ├── matrix: MatrixCalculator      ← Composed (not inherited)
    ├── evaluate(expr)                ← Safe math expression evaluator
    ├── chain(start, *ops)            ← Pipeline of operations
    └── info()                        ← Status string
```

### `calculator_gui.py`

```
calculator_gui.py
│
├── DESIGN PATTERN CLASSES
│   ├── CalcCommand                   ← Command pattern
│   ├── CommandHistory                ← Command stack (undo support)
│   ├── HistorySubject                ← Observer subject
│   ├── ThemeStrategy (abstract)      ← Strategy base
│   │   ├── DarkBlueTheme
│   │   ├── DarkGreenTheme
│   │   ├── MidnightPurpleTheme
│   │   ├── SlateTheme
│   │   └── LightTheme
│   ├── ThemeContext                  ← Holds active theme strategy
│   └── TabFactory (abstract)         ← Factory Method base
│       ├── StandardTabFactory
│       ├── ScientificTabFactory
│       ├── StatisticsTabFactory
│       ├── FinancialTabFactory
│       └── MatrixTabFactory
│
├── MODULE-LEVEL SINGLETONS
│   ├── theme_ctx        = ThemeContext()
│   ├── history_subject  = HistorySubject()
│   ├── cmd_history      = CommandHistory()
│   └── pc               = PowerCalc()
│
├── CalculatorApp(CTk)                ← Main window
│   ├── Toolbar      (title + theme dropdown + history toggle)
│   ├── Display bar  (expression + result labels)
│   ├── Tab view     (5 tabs created via factories)
│   ├── Eval bar     (free-form expression input)
│   └── History panel (collapsible side panel)
│
└── TAB CLASSES
    ├── StandardTab      ← Number pad, basic ops, memory, undo
    ├── ScientificTab    ← Trig, log, roots, constants
    ├── StatisticsTab    ← Descriptive stats, percentile, correlation
    ├── FinancialTab     ← 8 financial formula inputs
    └── MatrixTab        ← Matrix A & B grids + operations
```

---

## 4. Design Patterns

This project implements **7 design patterns** across two files. Each pattern solves a specific problem.

---

### 4.1 Creational — Singleton

**Where:** `calculator .py` → `PowerCalc`

**Problem it solves:** The entire application — all 5 tabs, the eval bar, and the history panel — must share one calculator engine with one shared history and memory. Without Singleton, each part could accidentally create its own separate calculator, losing history.

**How it works:**
```python
class PowerCalc(FinancialCalculator):
    _instance = None

    def __new__(cls, precision=10):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance   # always returns the SAME object

    def __init__(self, precision=10):
        if getattr(self, "_initialised", False):
            return             # skip re-init on every call
        super().__init__(precision=precision)
        self.matrix = MatrixCalculator()
        self._initialised = True
```

**Proof it works:**
```python
a = PowerCalc()
b = PowerCalc()
assert a is b        # True — same object in memory
a.memory_store(99)
print(b.memory_recall())  # 99 — same state
```

---

### 4.2 Creational — Factory Method

**Where:** `calculator_gui.py` → `TabFactory` hierarchy

**Problem it solves:** `CalculatorApp` needs to create 5 different tab types. Without Factory Method, the app would have 5 hardcoded `if/elif` blocks and would need to be changed every time a tab is added or removed.

**How it works:**  
Each factory is a small class with one job — create its specific tab.

```python
class TabFactory:                        # Abstract creator
    tab_name: str = ""
    def create_tab(self, parent, app):
        raise NotImplementedError        # subclasses must implement

class StandardTabFactory(TabFactory):   # Concrete creator
    tab_name = "Standard"
    def create_tab(self, parent, app):
        return StandardTab(parent, app)  # creates the product
```

`CalculatorApp` uses only the abstract interface — it never mentions `StandardTab` directly:
```python
for factory in TAB_FACTORIES:
    self._tabs.add(factory.tab_name)
    ctrl = factory.create_tab(self._tabs.tab(factory.tab_name), self)
```

To add a new tab, just add a new factory class and one entry in `TAB_FACTORIES`. No other code changes needed.

---

### 4.3 Behavioral — Command

**Where:** `calculator_gui.py` → `CalcCommand`, `CommandHistory`

**Problem it solves:** The Undo button needs to reverse a calculation without the button knowing what was calculated. The Command pattern wraps each calculation as an object that remembers how to undo itself.

**How it works:**
```python
class CalcCommand:
    def __init__(self, label, fn, prev_value):
        self.fn = fn                  # the calculation to run
        self.prev_value = prev_value  # what was on screen before

    def execute(self):
        self.result = self.fn()       # run the calculation
        return self.result

    def undo(self):
        return self.prev_value        # restore the old display value
```

**Usage in the Standard tab:**
```python
cmd = CalcCommand("10 + 5", lambda: pc.add(10, 5), prev_display)
result = cmd.execute()     # runs: pc.add(10, 5) → 15
cmd_history.push(cmd)      # save to stack

# When user clicks Undo:
prev = cmd_history.undo()  # pops command, returns prev_display
```

---

### 4.4 Behavioral — Observer

**Where:** `calculator_gui.py` → `HistorySubject`

**Problem it solves:** When a calculation finishes, two separate UI components need to update — the display bar and the history panel. Without Observer, the calculation code would need direct references to both widgets, creating tight coupling.

**How it works:**  
Components subscribe to `HistorySubject`. When any calculation calls `notify()`, all subscribers are updated automatically.

```python
class HistorySubject:
    def subscribe(self, fn):               # register a listener
        self._observers.append(fn)

    def notify(self, entry, expr, result): # broadcast to all listeners
        for fn in self._observers:
            fn(entry, expr, result)
```

**Who subscribes:**

| Subscriber | What it does when notified |
|---|---|
| `_on_calc_display` | Updates the expression and result labels at the top |
| `_on_calc_history` | Adds the new entry to the history side panel |

**Every tab calls this one line after every calculation:**
```python
history_subject.notify(f"{label} = {result}", label, result)
```

The tab does not know or care about the display or history panel — it just fires the event.

---

### 4.5 Behavioral — Strategy

**Where:** `calculator_gui.py` → `ThemeStrategy`, `ThemeContext`

**Problem it solves:** The app has 5 colour themes that can be switched at runtime. Without Strategy, you'd need long `if/elif` chains every time a colour is needed. With Strategy, each theme is a self-contained object and swapping themes is one line.

**How it works:**
```python
class ThemeStrategy:                  # Abstract strategy
    def colours(self) -> dict: ...

class DarkBlueTheme(ThemeStrategy):   # Concrete strategy
    name = "Dark Blue"
    def colours(self):
        return {"BG": "#1a1a2e", "ACCENT": "#1f6aa5", ...}

class ThemeContext:
    def set_strategy(self, name):
        self._current = self._strategies[name]  # swap at runtime

    def c(self, key) -> str:
        return self._current.colours()[key]     # get any colour
```

**Available themes:**

| Theme | Mode |
|---|---|
| Dark Blue | Dark |
| Dark Green | Dark |
| Midnight Purple | Dark |
| Slate | Dark |
| Light | Light |

---

### 4.6 Structural — Facade

**Where:** `calculator .py` → `PowerCalc`

**Problem it solves:** The engine has 5 classes with 40+ methods spread across an inheritance chain. The GUI shouldn't need to know which class provides which method. `PowerCalc` acts as a single front door to everything.

**How it works:**  
The GUI uses one object (`pc`) for everything:
```python
pc = PowerCalc()

pc.add(3, 5)                          # arithmetic (Calculator)
pc.sin(pc.PI / 2)                     # scientific  (ScientificCalculator)
pc.mean([1, 2, 3, 4, 5])             # statistical (StatisticalCalculator)
pc.compound_interest(1000, 0.05, 12, 3)  # financial (FinancialCalculator)
pc.matrix.determinant([[1,2],[3,4]])  # matrix     (MatrixCalculator)
pc.evaluate("2**8 + sqrt(36)")        # expression evaluator
```

Without the Facade, the GUI would need to import and manage 5 separate classes.

---

### 4.7 Behavioral — Template Method

**Where:** `calculator .py` → `Calculator._record()`

**Problem it solves:** Every single operation across all 40+ methods must do the same two things: log the result to history, then return it. Repeating this logic in every method would be error-prone and hard to maintain.

**How it works:**  
The base class defines the template once:
```python
def _record(self, expression: str, result) -> Number:
    self.history.append((expression, result))  # step 1: log
    return result                               # step 2: return
```

Every method in every subclass just calls `_record`:
```python
def add(self, a, b):
    return self._record(f"{a} + {b}", a + b)

def sin(self, x):
    return self._record(f"sin({x})", math.sin(x))

def mean(self, data):
    return self._record(f"mean({data})", statistics.mean(data))
```

To change how logging works (e.g. add timestamps), you only need to edit `_record` in one place.

---

## 5. Class Reference — Engine (`calculator .py`)

### `Calculator` — Base Class

| Method | Parameters | Returns | Description |
|---|---|---|---|
| `add` | `a, b` | Number | a + b |
| `subtract` | `a, b` | Number | a - b |
| `multiply` | `a, b` | Number | a × b |
| `divide` | `a, b` | Number | a ÷ b (raises error if b = 0) |
| `floor_divide` | `a, b` | Number | Integer division a // b |
| `modulo` | `a, b` | Number | Remainder a % b |
| `power` | `base, exp` | Number | base raised to exp |
| `absolute` | `a` | Number | Absolute value |
| `negate` | `a` | Number | Negative of a |
| `memory_store` | `value` | None | Save value to memory |
| `memory_recall` | — | float | Read stored memory value |
| `memory_clear` | — | None | Reset memory to 0 |
| `memory_add` | `value` | None | Add value to memory |
| `clear_history` | — | None | Erase all history entries |
| `show_history` | — | List[str] | Return history as text lines |

---

### `ScientificCalculator(Calculator)`

| Method | Parameters | Description |
|---|---|---|
| `sin / cos / tan` | `angle_rad` | Trigonometric functions (input must be in radians) |
| `asin / acos / atan` | `x` | Inverse trig (output in radians) |
| `sinh / cosh / tanh` | `x` | Hyperbolic functions |
| `log` | `x, base=e` | Logarithm to any base (default: natural log) |
| `log10 / log2` | `x` | Base-10 and base-2 logarithms |
| `exp` | `x` | e raised to the power x |
| `sqrt` | `x` | Square root (x must be ≥ 0) |
| `cbrt` | `x` | Cube root (works for negative x) |
| `nth_root` | `x, n` | x to the power of 1/n |
| `factorial` | `n` | n! (n must be a non-negative integer) |
| `permutation` | `n, r` | P(n,r) = n! / (n-r)! |
| `combination` | `n, r` | C(n,r) = n! / (r! × (n-r)!) |
| `PI / E / TAU / PHI` | — | Mathematical constants (read-only properties) |

---

### `StatisticalCalculator(ScientificCalculator)`

| Method | Parameters | Description |
|---|---|---|
| `mean` | `data` | Average of all values |
| `median` | `data` | Middle value when sorted |
| `mode` | `data` | Most frequently occurring value |
| `std_dev` | `data, population=False` | Standard deviation (sample by default) |
| `variance` | `data, population=False` | Variance (sample by default) |
| `data_range` | `data` | max − min |
| `percentile` | `data, p` | Value at the p-th percentile (0–100) |
| `correlation` | `x, y` | Pearson correlation coefficient |
| `sum_data` | `data` | Sum of all values |
| `product_data` | `data` | Product of all values |
| `geometric_mean` | `data` | nth root of the product of all values |
| `harmonic_mean` | `data` | n divided by the sum of reciprocals |

---

### `FinancialCalculator(StatisticalCalculator)`

| Method | Formula | Description |
|---|---|---|
| `simple_interest(P, r, t)` | P × r × t | Total interest earned |
| `compound_interest(P, r, n, t)` | P(1 + r/n)^(nt) | Final amount after compounding |
| `present_value(FV, r, n)` | FV / (1+r)^n | Current worth of a future amount |
| `future_value(PV, r, n)` | PV × (1+r)^n | Value of money after growth |
| `loan_payment(P, r, y)` | PMT formula | Monthly payment on a loan |
| `roi(gain, cost)` | (gain−cost)/cost × 100 | Return on investment as a percentage |
| `break_even(FC, P, VC)` | FC / (P − VC) | Units needed to cover fixed costs |
| `inflation_adjusted(A, i, y)` | A / (1+i)^y | Real value after inflation |

---

### `MatrixCalculator` — Standalone Class

| Method | Description |
|---|---|
| `add(A, B)` | Add two matrices element by element |
| `subtract(A, B)` | Subtract B from A element by element |
| `multiply(A, B)` | Standard matrix multiplication |
| `scalar_multiply(A, k)` | Multiply every element by scalar k |
| `transpose(A)` | Flip rows and columns |
| `determinant(A)` | Calculate the determinant (uses LU decomposition) |
| `identity(n)` | Create an n×n identity matrix |
| `trace(A)` | Sum of the main diagonal elements |
| `flatten(A)` | Convert 2D matrix to a flat 1D list |

---

### `PowerCalc(FinancialCalculator)` — Singleton + Facade

| Member | Description |
|---|---|
| `VERSION` | Current version string: `"2.0.0"` |
| `matrix` | Attached `MatrixCalculator` instance |
| `evaluate(expr)` | Safely evaluate a math expression string |
| `chain(start, *ops)` | Run a pipeline: `chain(10, ('add',5), ('sqrt',))` |
| `info()` | Print version, history count, and memory value |

---

## 6. Class Reference — GUI (`calculator_gui.py`)

### Pattern Support Classes

| Class | Pattern | Key Methods |
|---|---|---|
| `CalcCommand` | Command | `execute()` — runs the calculation; `undo()` — returns previous value |
| `CommandHistory` | Command | `push(cmd)`, `undo()`, `clear()` |
| `HistorySubject` | Observer | `subscribe(fn)` — add a listener; `notify(entry, expr, result)` — broadcast |
| `ThemeStrategy` | Strategy | `colours() → dict` (abstract — must be overridden) |
| `ThemeContext` | Strategy | `set_strategy(name)`, `c(key)` — get a colour value |
| `TabFactory` | Factory Method | `create_tab(parent, app)` (abstract — must be overridden) |

---

### Theme Strategies

| Class | Appearance | Primary Accent |
|---|---|---|
| `DarkBlueTheme` | Dark | `#1f6aa5` (blue) |
| `DarkGreenTheme` | Dark | `#2d8a4e` (green) |
| `MidnightPurpleTheme` | Dark | `#8a2be2` (purple) |
| `SlateTheme` | Dark | `#5b9bd5` (light blue) |
| `LightTheme` | Light | `#1f6aa5` (blue) |

---

### Tab Factories

| Factory Class | Tab Created | Tab Contents |
|---|---|---|
| `StandardTabFactory` | `StandardTab` | Number pad, basic operations, memory buttons, Undo |
| `ScientificTabFactory` | `ScientificTab` | Trig, logarithms, roots, math constants |
| `StatisticsTabFactory` | `StatisticsTab` | Descriptive statistics, percentile, correlation |
| `FinancialTabFactory` | `FinancialTab` | 8 financial formula input forms |
| `MatrixTabFactory` | `MatrixTab` | Two matrix input grids and operations |

---

### `CalculatorApp(CTk)` — Main Window

| Method | Description |
|---|---|
| `_build_layout()` | Sets up the 4-row, 2-column grid layout |
| `_build_toolbar()` | Creates title label, theme dropdown, and history toggle button |
| `_build_display()` | Creates the expression and result labels at the top |
| `_build_tabs()` | Uses TAB_FACTORIES to create all 5 tabs |
| `_build_eval_bar()` | Creates the free-form expression input bar at the bottom |
| `_build_history_panel()` | Creates the collapsible 260px history side panel |
| `_toggle_history()` | Shows or hides the history panel |
| `_switch_theme(name)` | Swaps the theme strategy and rebuilds the entire UI |
| `_on_calc_display(e,x,r)` | Observer callback: updates the display bar |
| `_on_calc_history(e,x,r)` | Observer callback: adds entry to history panel |
| `_refresh_history_panel()` | Redraws all history entries in the scroll panel |
| `_clear_history()` | Clears history entries and the command undo stack |
| `_run_eval()` | Evaluates the expression in the eval bar using Command pattern |
| `set_display(expr, result)` | Called by tabs to update the display labels |
| `get_result()` | Returns the current result string from the display |

---

## 7. Data Flow

### Standard Calculation (pressing "=")

```
User presses "=" button
        │
        ▼
StandardTab._equals()
        │
        ├── Builds the full expression string
        ├── Creates: CalcCommand(label, fn, prev_display)   [COMMAND]
        ├── Calls:   cmd.execute()  →  pc.evaluate(expr)    [ENGINE]
        ├── Pushes:  cmd_history.push(cmd)                  [UNDO STACK]
        │
        └── Calls: history_subject.notify(entry, expr, result)  [OBSERVER]
                          │
                          ├──► _on_calc_display()  → updates top display bar
                          └──► _on_calc_history()  → adds entry to history panel
```

### Undo Operation

```
User clicks "⟲ Undo"
        │
        ▼
StandardTab._undo()
        │
        ├── cmd_history.undo()   → pops the last CalcCommand from stack
        ├── cmd.undo()           → returns the previous display value
        └── app.set_display("(undo)", prev_value)  → restores old display
```

### Theme Switch

```
User selects a new theme from the dropdown
        │
        ▼
CalculatorApp._switch_theme(name)
        │
        ├── theme_ctx.set_strategy(name)   [STRATEGY SWAP]
        ├── Destroys all current widgets
        ├── _build_layout()                [REBUILD UI with new colours]
        │       └── _build_tabs()
        │               └── for factory in TAB_FACTORIES:  [FACTORY METHOD]
        │                       factory.create_tab(...)
        ├── history_subject._observers.clear()
        ├── history_subject.subscribe(...)  [RE-WIRE OBSERVERS]
        └── _refresh_history_panel()        [RESTORE HISTORY ENTRIES]
```

---

## 8. Component Interaction Diagram

```
┌───────────────────────────────────────────────────────────────────┐
│                        calculator_gui.py                           │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                      CalculatorApp                            │ │
│  │                                                               │ │
│  │  Toolbar ──── ThemeContext ──── ThemeStrategy  [Strategy]    │ │
│  │                                                               │ │
│  │  Display Bar ◄────────────────────────────────────────────┐  │ │
│  │                                                            │  │ │
│  │  TabView ──── TAB_FACTORIES ──── TabFactory  [Factory]    │  │ │
│  │                    │                                       │  │ │
│  │         ┌──────────┴──────────┐                           │  │ │
│  │    StandardTab          ScientificTab  ...                 │  │ │
│  │         │                                                  │  │ │
│  │    CalcCommand ──── CommandHistory       [Command]         │  │ │
│  │         │                                                  │  │ │
│  │    HistorySubject ─────────────────────────────────────►──┘  │ │
│  │    [Observer]     └──────────────────────► History Panel     │ │
│  │                                                               │ │
│  │  EvalBar ──── CalcCommand ──── CommandHistory                │ │
│  └──────────────────────┬────────────────────────────────────────┘ │
│                         │  calls                                    │
└─────────────────────────┼──────────────────────────────────────────┘
                          │
┌─────────────────────────▼──────────────────────────────────────────┐
│                        calculator .py                               │
│                                                                     │
│   PowerCalc  (Singleton + Facade)                                   │
│     ├── evaluate()  chain()  info()                                 │
│     ├── FinancialCalculator                                         │
│     │     └── StatisticalCalculator                                 │
│     │           └── ScientificCalculator                            │
│     │                 └── Calculator  ← _record()  [Template Method]│
│     └── MatrixCalculator  (composed)                                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 9. How to Run

### Requirements

- Python 3.8 or later
- `customtkinter` library

### Install dependencies

```bash
pip install customtkinter
```

### Run the GUI application

```bash
python calculator_gui.py
```

### Run the engine demo (no GUI)

```bash
python "calculator .py"
```

### Quick engine usage in your own script

```python
from importlib.util import spec_from_file_location, module_from_spec

spec = spec_from_file_location("calculator", "calculator .py")
mod = module_from_spec(spec)
spec.loader.exec_module(mod)

pc = mod.PowerCalc()
print(pc.add(3, 5))           # 8
print(pc.sin(pc.PI / 2))      # 1.0
print(pc.mean([1,2,3,4,5]))   # 3
```

---

*Software Architecture Design Project — PowerCalc 2.0*
