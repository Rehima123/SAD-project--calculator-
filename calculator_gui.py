"""
calculator_gui.py  —  PowerCalc GUI (customtkinter)
====================================================

DESIGN PATTERNS USED
--------------------

PATTERN 1 — COMMAND (Behavioral)
  Every calculation is wrapped in a CalcCommand object that stores the
  callable, its result, and the previous display value.  A CommandHistory
  stack lets the Standard-tab Undo button walk back through operations
  without the UI needing to know anything about the calculation logic.

PATTERN 2 — OBSERVER (Behavioral)
  HistorySubject holds a list of subscriber callbacks.  When any
  calculation completes it calls history_subject.notify(entry, expr, result).
  The history panel and the display bar each subscribe independently, so
  the calculation code never references UI widgets directly.

PATTERN 3 — STRATEGY (Behavioral)
  Each colour theme is a concrete ThemeStrategy subclass that returns a
  colour dict.  ThemeContext holds the active strategy and exposes theme_ctx.c()
  for colour look-ups.  Switching themes at runtime just swaps the strategy
  object and rebuilds the UI — no if/elif chains anywhere.
"""

# ── stdlib ──────────────────────────────────────────────────────────────────
import math
import importlib
import importlib.util
import sys
import os

# ── third-party ─────────────────────────────────────────────────────────────
import customtkinter as ctk

# ── local — note the space in the filename ──────────────────────────────────
_spec = importlib.util.spec_from_file_location(
    "calculator",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "calculator .py"),
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
PowerCalc = _mod.PowerCalc

# ─────────────────────────────────────────────────────────────────────────────
# PATTERN 1 — COMMAND
# ─────────────────────────────────────────────────────────────────────────────

class CalcCommand:
    """
    Encapsulates a single calculation as a command object.
    execute() runs the callable and stores the result.
    undo()    returns the value that was on the display before this command.
    """
    def __init__(self, label: str, fn, prev_value: str):
        self.label = label
        self.fn = fn                # callable that returns the result
        self.result = None
        self.prev_value = prev_value

    def execute(self):
        self.result = self.fn()
        return self.result

    def undo(self):
        return self.prev_value


class CommandHistory:
    """Manages a stack of CalcCommand objects for undo support."""
    def __init__(self):
        self._stack = []

    def push(self, cmd: CalcCommand):
        self._stack.append(cmd)

    def undo(self):
        if self._stack:
            return self._stack.pop().undo()
        return None

    def clear(self):
        self._stack.clear()


# ─────────────────────────────────────────────────────────────────────────────
# PATTERN 2 — OBSERVER
# ─────────────────────────────────────────────────────────────────────────────

class HistorySubject:
    """
    Subject in the Observer pattern.
    Any UI component can subscribe; when a calculation completes,
    notify() broadcasts the result to all subscribers automatically.
    """
    def __init__(self):
        self._observers = []

    def subscribe(self, fn):
        self._observers.append(fn)

    def notify(self, entry: str, expr: str, result: str):
        for fn in self._observers:
            fn(entry, expr, result)


# ─────────────────────────────────────────────────────────────────────────────
# PATTERN 3 — STRATEGY  (themes)
# ─────────────────────────────────────────────────────────────────────────────

class ThemeStrategy:
    """Abstract base strategy — subclasses return a colour dict."""
    name = "Base"
    def colours(self) -> dict:
        raise NotImplementedError


class DarkBlueTheme(ThemeStrategy):
    name = "Dark Blue"
    def colours(self):
        return {
            "appearance": "dark", "ctk_theme": "blue",
            "BG": "#1a1a2e", "PANEL": "#16213e", "CARD": "#0f3460",
            "ACCENT": "#1f6aa5", "ACCENT2": "#e94560",
            "TEXT": "#e0e0e0", "SUBTEXT": "#a0a0b0",
            "BTN_NUM": "#1e2a45", "BTN_OP": "#1f3a6e", "BTN_EQ": "#1f6aa5",
            "BTN_SPEC": "#0d2137", "BTN_MEM": "#162032",
            "HOVER_NUM": "#2a3a5e", "HOVER_OP": "#2a4a8e", "HOVER_EQ": "#2a7ac5",
        }


class DarkGreenTheme(ThemeStrategy):
    name = "Dark Green"
    def colours(self):
        return {
            "appearance": "dark", "ctk_theme": "green",
            "BG": "#0d1f0d", "PANEL": "#122212", "CARD": "#1a3a1a",
            "ACCENT": "#2d8a4e", "ACCENT2": "#e94560",
            "TEXT": "#e0f0e0", "SUBTEXT": "#90b090",
            "BTN_NUM": "#1a2e1a", "BTN_OP": "#1e3e1e", "BTN_EQ": "#2d8a4e",
            "BTN_SPEC": "#0d1f0d", "BTN_MEM": "#111e11",
            "HOVER_NUM": "#2a3e2a", "HOVER_OP": "#2a4e2a", "HOVER_EQ": "#3aaa60",
        }


class MidnightPurpleTheme(ThemeStrategy):
    name = "Midnight Purple"
    def colours(self):
        return {
            "appearance": "dark", "ctk_theme": "blue",
            "BG": "#12001f", "PANEL": "#1a0030", "CARD": "#2a0050",
            "ACCENT": "#8a2be2", "ACCENT2": "#ff4d6d",
            "TEXT": "#f0e0ff", "SUBTEXT": "#b090d0",
            "BTN_NUM": "#1e0035", "BTN_OP": "#2a0050", "BTN_EQ": "#8a2be2",
            "BTN_SPEC": "#0d0020", "BTN_MEM": "#150028",
            "HOVER_NUM": "#2e0050", "HOVER_OP": "#3a0070", "HOVER_EQ": "#a040ff",
        }


class SlateTheme(ThemeStrategy):
    name = "Slate"
    def colours(self):
        return {
            "appearance": "dark", "ctk_theme": "blue",
            "BG": "#1c1c1c", "PANEL": "#252525", "CARD": "#2e2e2e",
            "ACCENT": "#5b9bd5", "ACCENT2": "#e05c5c",
            "TEXT": "#e8e8e8", "SUBTEXT": "#999999",
            "BTN_NUM": "#2a2a2a", "BTN_OP": "#333333", "BTN_EQ": "#5b9bd5",
            "BTN_SPEC": "#1e1e1e", "BTN_MEM": "#222222",
            "HOVER_NUM": "#3a3a3a", "HOVER_OP": "#444444", "HOVER_EQ": "#70aee0",
        }


class LightTheme(ThemeStrategy):
    name = "Light"
    def colours(self):
        return {
            "appearance": "light", "ctk_theme": "blue",
            "BG": "#f0f4f8", "PANEL": "#ffffff", "CARD": "#dce8f5",
            "ACCENT": "#1f6aa5", "ACCENT2": "#e94560",
            "TEXT": "#1a1a2e", "SUBTEXT": "#555577",
            "BTN_NUM": "#e8eef5", "BTN_OP": "#ccddf0", "BTN_EQ": "#1f6aa5",
            "BTN_SPEC": "#d8e8f8", "BTN_MEM": "#e0eaf5",
            "HOVER_NUM": "#d0dcea", "HOVER_OP": "#b8ccdf", "HOVER_EQ": "#2a7ac5",
        }


class ThemeContext:
    """
    Holds the active ThemeStrategy and exposes c() for colour look-ups.
    Switching themes calls set_strategy() — no if/elif chains needed.
    """
    _strategies = {
        s.name: s for s in [
            DarkBlueTheme(), DarkGreenTheme(), MidnightPurpleTheme(),
            SlateTheme(), LightTheme(),
        ]
    }

    def __init__(self):
        self._current = DarkBlueTheme()

    def set_strategy(self, name: str):
        self._current = self._strategies[name]
        ctk.set_appearance_mode(self._current.colours()["appearance"])

    def c(self, key: str) -> str:
        return self._current.colours()[key]

    @property
    def name(self):
        return self._current.name

    @property
    def names(self):
        return list(self._strategies.keys())


# ─────────────────────────────────────────────────────────────────────────────
# MODULE-LEVEL SINGLETONS
# ─────────────────────────────────────────────────────────────────────────────

theme_ctx       = ThemeContext()          # Strategy singleton
history_subject = HistorySubject()        # Observer singleton
cmd_history     = CommandHistory()        # Command singleton
pc              = PowerCalc()             # Calculator engine  (Singleton)


# ─────────────────────────────────────────────────────────────────────────────
# CREATIONAL PATTERN 2 — FACTORY METHOD
# ─────────────────────────────────────────────────────────────────────────────
#
# TabFactory defines the interface (create_tab) for producing calculator tab
# objects.  Each concrete factory knows exactly which class to instantiate and
# how to wire it up.  CalculatorApp calls TabFactory.create_tab() and never
# references the concrete tab classes directly — it is fully decoupled from
# the creation logic.
#
#   TabFactory  (abstract creator)
#       ├── StandardTabFactory   → StandardTab
#       ├── ScientificTabFactory → ScientificTab
#       ├── StatisticsTabFactory → StatisticsTab
#       ├── FinancialTabFactory  → FinancialTab
#       └── MatrixTabFactory     → MatrixTab
# ─────────────────────────────────────────────────────────────────────────────

class TabFactory:
    """Abstract creator — subclasses override create_tab()."""
    tab_name: str = ""

    def create_tab(self, parent, app):
        """Factory Method: produce and return a tab controller object."""
        raise NotImplementedError


class StandardTabFactory(TabFactory):
    tab_name = "Standard"
    def create_tab(self, parent, app):
        return StandardTab(parent, app)


class ScientificTabFactory(TabFactory):
    tab_name = "Scientific"
    def create_tab(self, parent, app):
        return ScientificTab(parent, app)


class StatisticsTabFactory(TabFactory):
    tab_name = "Statistics"
    def create_tab(self, parent, app):
        return StatisticsTab(parent, app)


class FinancialTabFactory(TabFactory):
    tab_name = "Financial"
    def create_tab(self, parent, app):
        return FinancialTab(parent, app)


class MatrixTabFactory(TabFactory):
    tab_name = "Matrix"
    def create_tab(self, parent, app):
        return MatrixTab(parent, app)


# Ordered registry — CalculatorApp iterates this to build all tabs
TAB_FACTORIES = [
    StandardTabFactory(),
    ScientificTabFactory(),
    StatisticsTabFactory(),
    FinancialTabFactory(),
    MatrixTabFactory(),
]


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def fmt(value) -> str:
    """Format a calculation result for display."""
    if isinstance(value, float):
        if value == int(value) and abs(value) < 1e15:
            return str(int(value))
        return f"{value:.10g}"
    if isinstance(value, list):
        rows = ["  [" + "  ".join(f"{v:.6g}" for v in row) + "]" for row in value]
        return "[\n" + "\n".join(rows) + "\n]"
    return str(value)


def mk_btn(parent, text, cmd, fg, hover, text_color=None,
           font_size=14, height=52, colspan=1, row=0, col=0):
    """Create and grid a styled CTkButton."""
    b = ctk.CTkButton(
        parent, text=text, command=cmd,
        fg_color=fg, hover_color=hover,
        font=ctk.CTkFont(size=font_size, weight="bold"),
        text_color=text_color or theme_ctx.c("TEXT"),
        corner_radius=8, height=height,
    )
    b.grid(row=row, column=col, columnspan=colspan,
           padx=3, pady=3, sticky="nsew")
    return b

# ─────────────────────────────────────────────────────────────────────────────
# MAIN APPLICATION WINDOW
# ─────────────────────────────────────────────────────────────────────────────

class CalculatorApp(ctk.CTk):
    """Root window — builds toolbar, display bar, tab view, eval bar, history panel."""

    def __init__(self):
        ctk.set_appearance_mode(theme_ctx.c("appearance"))
        ctk.set_default_color_theme(theme_ctx.c("ctk_theme"))
        super().__init__()

        self.title("Calculator")
        self.geometry("1050x780")
        self.minsize(900, 700)
        self.configure(fg_color=theme_ctx.c("BG"))

        self._history_visible = False
        self._history_entries = []   # list of strings, newest first

        self._build_layout()

        # ── Observer subscriptions ──────────────────────────────────────────
        # Display bar subscribes to update expr/result labels
        history_subject.subscribe(self._on_calc_display)
        # History panel subscribes to refresh its list
        history_subject.subscribe(self._on_calc_history)

        # Keyboard bindings for Standard tab
        self.bind("<Key>", self._on_key)

    # ── Layout construction ──────────────────────────────────────────────────

    def _build_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0, minsize=0)
        self.grid_rowconfigure(0, weight=0, minsize=46)
        self.grid_rowconfigure(1, weight=0, minsize=90)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=0, minsize=48)

        self._build_toolbar()
        self._build_display()
        self._build_tabs()
        self._build_eval_bar()
        self._build_history_panel()

    def _build_toolbar(self):
        bar = ctk.CTkFrame(self, fg_color=theme_ctx.c("PANEL"), height=46, corner_radius=0)
        bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        bar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            bar, text="🧮 Calculator",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=theme_ctx.c("ACCENT"),
        ).grid(row=0, column=0, padx=16, pady=6, sticky="w")

        # ── Strategy pattern: theme dropdown ─────────────────────────────────
        self._theme_var = ctk.StringVar(value=theme_ctx.name)
        theme_menu = ctk.CTkOptionMenu(
            bar,
            values=theme_ctx.names,
            variable=self._theme_var,
            command=self._switch_theme,
            fg_color=theme_ctx.c("CARD"),
            button_color=theme_ctx.c("ACCENT"),
            button_hover_color=theme_ctx.c("HOVER_EQ"),
            text_color=theme_ctx.c("TEXT"),
            font=ctk.CTkFont(size=13),
            width=170,
        )
        theme_menu.grid(row=0, column=1, padx=8, pady=6, sticky="e")

        self._hist_toggle_btn = ctk.CTkButton(
            bar, text="📋 History", width=120,
            fg_color=theme_ctx.c("BTN_SPEC"),
            hover_color=theme_ctx.c("HOVER_NUM"),
            text_color=theme_ctx.c("TEXT"),
            font=ctk.CTkFont(size=13),
            command=self._toggle_history,
        )
        self._hist_toggle_btn.grid(row=0, column=2, padx=12, pady=6, sticky="e")

    def _build_display(self):
        self._display_frame = ctk.CTkFrame(
            self, fg_color=theme_ctx.c("PANEL"), height=90, corner_radius=0,
        )
        self._display_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        self._display_frame.grid_columnconfigure(0, weight=1)

        self._expr_var   = ctk.StringVar(value="")
        self._result_var = ctk.StringVar(value="0")

        ctk.CTkLabel(
            self._display_frame,
            textvariable=self._expr_var,
            font=ctk.CTkFont(size=13),
            text_color=theme_ctx.c("SUBTEXT"),
            anchor="e",
        ).grid(row=0, column=0, padx=18, pady=(10, 0), sticky="ew")

        ctk.CTkLabel(
            self._display_frame,
            textvariable=self._result_var,
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=theme_ctx.c("TEXT"),
            anchor="e",
        ).grid(row=1, column=0, padx=18, pady=(0, 8), sticky="ew")

    def _build_tabs(self):
        self._tabs = ctk.CTkTabview(
            self,
            fg_color=theme_ctx.c("BG"),
            segmented_button_fg_color=theme_ctx.c("PANEL"),
            segmented_button_selected_color=theme_ctx.c("ACCENT"),
            segmented_button_selected_hover_color=theme_ctx.c("HOVER_EQ"),
            segmented_button_unselected_color=theme_ctx.c("PANEL"),
            segmented_button_unselected_hover_color=theme_ctx.c("CARD"),
            text_color=theme_ctx.c("TEXT"),
        )
        self._tabs.grid(row=2, column=0, sticky="nsew", padx=0, pady=0)

        # ── Factory Method pattern: each factory creates its own tab ──────────
        # CalculatorApp never references concrete tab classes directly.
        self._tab_controllers = {}
        for factory in TAB_FACTORIES:
            self._tabs.add(factory.tab_name)
            ctrl = factory.create_tab(self._tabs.tab(factory.tab_name), self)
            self._tab_controllers[factory.tab_name] = ctrl

        # Convenience aliases used by keyboard handler
        self._std_tab = self._tab_controllers["Standard"]

    def _build_eval_bar(self):
        bar = ctk.CTkFrame(self, fg_color=theme_ctx.c("PANEL"), height=48, corner_radius=0)
        bar.grid(row=3, column=0, columnspan=2, sticky="ew")
        bar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            bar, text="Eval:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=theme_ctx.c("SUBTEXT"),
        ).grid(row=0, column=0, padx=(14, 6), pady=8)

        self._eval_entry = ctk.CTkEntry(
            bar,
            fg_color=theme_ctx.c("CARD"),
            border_color=theme_ctx.c("ACCENT"),
            text_color=theme_ctx.c("TEXT"),
            font=ctk.CTkFont(size=14),
            placeholder_text="e.g.  2**8 + sqrt(36)",
        )
        self._eval_entry.grid(row=0, column=1, padx=4, pady=8, sticky="ew")
        self._eval_entry.bind("<Return>", lambda _e: self._run_eval())

        ctk.CTkButton(
            bar, text="=", width=52,
            fg_color=theme_ctx.c("BTN_EQ"),
            hover_color=theme_ctx.c("HOVER_EQ"),
            text_color=theme_ctx.c("TEXT"),
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self._run_eval,
        ).grid(row=0, column=2, padx=(4, 14), pady=8)

    def _build_history_panel(self):
        self._hist_panel = ctk.CTkFrame(
            self, fg_color=theme_ctx.c("PANEL"), width=260, corner_radius=0,
        )
        self._hist_panel.grid_propagate(False)   # enforce fixed width=260
        # Not gridded yet — shown on toggle

        self._hist_panel.grid_rowconfigure(1, weight=1)
        self._hist_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self._hist_panel,
            text="History",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=theme_ctx.c("ACCENT"),
        ).grid(row=0, column=0, padx=10, pady=(10, 4), sticky="w")

        self._hist_scroll = ctk.CTkScrollableFrame(
            self._hist_panel,
            fg_color=theme_ctx.c("BG"),
            width=230,
        )
        self._hist_scroll.grid(row=1, column=0, padx=6, pady=4, sticky="nsew")
        self._hist_panel.grid_rowconfigure(1, weight=1)

        ctk.CTkButton(
            self._hist_panel,
            text="Clear History",
            fg_color=theme_ctx.c("ACCENT2"),
            hover_color="#c03050",
            text_color="#ffffff",
            font=ctk.CTkFont(size=12),
            command=self._clear_history,
        ).grid(row=2, column=0, padx=10, pady=(4, 10), sticky="ew")

    # ── Observer callbacks ───────────────────────────────────────────────────

    def _on_calc_display(self, entry: str, expr: str, result: str):
        """Observer: update the display bar when a calculation completes."""
        self._expr_var.set(expr)
        self._result_var.set(result)

    def _on_calc_history(self, entry: str, expr: str, result: str):
        """Observer: prepend a new entry to the history panel."""
        self._history_entries.insert(0, entry)
        if len(self._history_entries) > 50:
            self._history_entries = self._history_entries[:50]
        self._refresh_history_panel()

    def _refresh_history_panel(self):
        for w in self._hist_scroll.winfo_children():
            w.destroy()
        for i, entry in enumerate(self._history_entries):
            bg = theme_ctx.c("CARD") if i % 2 == 0 else theme_ctx.c("PANEL")
            ctk.CTkLabel(
                self._hist_scroll,
                text=entry,
                font=ctk.CTkFont(size=11),
                text_color=theme_ctx.c("TEXT"),
                fg_color=bg,
                anchor="w",
                wraplength=210,
                justify="left",
            ).pack(fill="x", padx=2, pady=1)

    def _clear_history(self):
        self._history_entries.clear()
        cmd_history.clear()
        self._refresh_history_panel()

    # ── History panel toggle ─────────────────────────────────────────────────

    def _toggle_history(self):
        if self._history_visible:
            self._hist_panel.grid_forget()
            self.grid_columnconfigure(1, weight=0, minsize=0)
            self._hist_toggle_btn.configure(text="📋 History", fg_color=theme_ctx.c("BTN_SPEC"))
            self._history_visible = False
        else:
            self._hist_panel.grid(row=1, column=1, rowspan=3, sticky="nsew", padx=(4,8), pady=0)
            self.grid_columnconfigure(1, weight=0, minsize=260)
            self._hist_toggle_btn.configure(text="✕ History", fg_color=theme_ctx.c("ACCENT"))
            self._history_visible = True

    # ── Strategy: theme switching ────────────────────────────────────────────

    def _switch_theme(self, name: str):
        """Strategy pattern: swap the active ThemeStrategy and rebuild the UI."""
        theme_ctx.set_strategy(name)
        # Rebuild by destroying and recreating all widgets
        for w in self.winfo_children():
            w.destroy()
        self._history_visible = False
        self._build_layout()
        # Re-subscribe observers — clear first to prevent duplicates on theme switch
        history_subject._observers.clear()
        history_subject.subscribe(self._on_calc_display)
        history_subject.subscribe(self._on_calc_history)
        self._refresh_history_panel()

    # ── Eval bar ─────────────────────────────────────────────────────────────

    def _run_eval(self):
        expr = self._eval_entry.get().strip()
        if not expr:
            return
        prev = self._result_var.get()

        # Command pattern: wrap evaluation in a CalcCommand
        def _do():
            return pc.evaluate(expr)

        cmd = CalcCommand(f"eval: {expr}", _do, prev)
        try:
            result = cmd.execute()
            cmd_history.push(cmd)
            r_str = fmt(result)
            history_subject.notify(f"{expr} = {r_str}", expr, r_str)
        except Exception as ex:
            self._result_var.set(f"Error: {ex}")

    # ── Keyboard handler (delegates to Standard tab) ─────────────────────────

    def _on_key(self, event):
        if self._tabs.get() == "Standard":
            self._std_tab.handle_key(event)

    # ── Public helpers used by tabs ──────────────────────────────────────────

    def set_display(self, expr: str, result: str):
        self._expr_var.set(expr)
        self._result_var.set(result)

    def get_result(self) -> str:
        return self._result_var.get()

# ─────────────────────────────────────────────────────────────────────────────
# STANDARD TAB
# ─────────────────────────────────────────────────────────────────────────────

class StandardTab:
    """
    Classic calculator layout.
    Uses Command pattern for every = press and Undo button.
    """

    def __init__(self, parent, app: CalculatorApp):
        self.app = app
        self.parent = parent
        parent.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self._expr   = ""   # accumulating expression string
        self._input  = ""   # current token being typed

        # Mini expression display
        self._expr_var = ctk.StringVar(value="")
        ctk.CTkLabel(
            parent,
            textvariable=self._expr_var,
            font=ctk.CTkFont(size=12),
            text_color=theme_ctx.c("SUBTEXT"),
            anchor="e",
        ).grid(row=0, column=0, columnspan=4, padx=8, pady=(6, 0), sticky="ew")

        self._build_buttons()

    def _build_buttons(self):
        p = self.parent
        C = theme_ctx.c

        # Row 0 — Memory
        mk_btn(p, "MS",  self._ms,  C("BTN_MEM"),  C("HOVER_NUM"), height=44, row=1, col=0)
        mk_btn(p, "MR",  self._mr,  C("BTN_MEM"),  C("HOVER_NUM"), height=44, row=1, col=1)
        mk_btn(p, "MC",  self._mc,  C("BTN_MEM"),  C("HOVER_NUM"), height=44, row=1, col=2)
        mk_btn(p, "M+",  self._mplus, C("BTN_MEM"), C("HOVER_NUM"), height=44, row=1, col=3)

        # Row 1 — Clear / ops / brackets
        mk_btn(p, "C",   self._clear,    C("ACCENT2"),  "#c03050",     height=52, row=2, col=0)
        mk_btn(p, "⌫",   self._backspace, C("BTN_SPEC"), C("HOVER_NUM"), height=52, row=2, col=1)
        mk_btn(p, "(",   lambda: self._bracket("("), C("BTN_OP"), C("HOVER_OP"), height=52, row=2, col=2)
        mk_btn(p, ")",   lambda: self._bracket(")"), C("BTN_OP"), C("HOVER_OP"), height=52, row=2, col=3)

        # Rows 2-4 — digits + ops
        digits_ops = [
            ("7", "8", "9", "×"),
            ("4", "5", "6", "−"),
            ("1", "2", "3", "+"),
        ]
        for r, row_data in enumerate(digits_ops):
            for c, label in enumerate(row_data):
                if label in ("×", "−", "+"):
                    sym = {"×": "*", "−": "-", "+": "+"}[label]
                    mk_btn(p, label, lambda s=sym: self._op(s),
                           theme_ctx.c("BTN_OP"), theme_ctx.c("HOVER_OP"),
                           height=52, row=r + 3, col=c)
                else:
                    mk_btn(p, label, lambda d=label: self._digit(d),
                           theme_ctx.c("BTN_NUM"), theme_ctx.c("HOVER_NUM"),
                           height=52, row=r + 3, col=c)

        # Row 5 — +/−, 0, ., =
        mk_btn(p, "+/−", self._negate,  theme_ctx.c("BTN_SPEC"), theme_ctx.c("HOVER_NUM"), height=52, row=6, col=0)
        mk_btn(p, "0",   lambda: self._digit("0"), theme_ctx.c("BTN_NUM"), theme_ctx.c("HOVER_NUM"), height=52, row=6, col=1)
        mk_btn(p, ".",   lambda: self._digit("."), theme_ctx.c("BTN_NUM"), theme_ctx.c("HOVER_NUM"), height=52, row=6, col=2)
        mk_btn(p, "=",   self._equals,  theme_ctx.c("BTN_EQ"),  theme_ctx.c("HOVER_EQ"),  height=52, row=6, col=3)

        # Row 6 — extra ops
        mk_btn(p, "%",   lambda: self._op("%"),  theme_ctx.c("BTN_OP"), theme_ctx.c("HOVER_OP"), font_size=13, height=44, row=7, col=0)
        mk_btn(p, "÷",   lambda: self._op("/"),  theme_ctx.c("BTN_OP"), theme_ctx.c("HOVER_OP"), font_size=13, height=44, row=7, col=1)
        mk_btn(p, "x²",  self._square,  theme_ctx.c("BTN_OP"), theme_ctx.c("HOVER_OP"), font_size=12, height=44, row=7, col=2)
        mk_btn(p, "√x",  self._sqrt,    theme_ctx.c("BTN_OP"), theme_ctx.c("HOVER_OP"), font_size=12, height=44, row=7, col=3)

        # Undo button — Command pattern
        undo_btn = ctk.CTkButton(
            p, text="⟲ Undo",
            command=self._undo,
            fg_color=theme_ctx.c("BTN_SPEC"),
            hover_color=theme_ctx.c("HOVER_NUM"),
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=theme_ctx.c("TEXT"),
            corner_radius=8, height=44,
        )
        undo_btn.grid(row=8, column=0, columnspan=4, padx=3, pady=3, sticky="ew")

        for r in range(1, 9):
            p.grid_rowconfigure(r, weight=1)

    # ── Input helpers ────────────────────────────────────────────────────────

    def _digit(self, d: str):
        if self.app.get_result().startswith("Error"):
            self._clear()
        self._input += d
        self._expr_var.set(self._expr + self._input)
        self.app.set_display(self._expr + self._input, self._input or "0")

    def _op(self, sym: str):
        if self._input:
            self._expr += self._input + f" {sym} "
            self._input = ""
        elif self._expr:
            # Replace last operator
            self._expr = self._expr.rstrip() 
            self._expr = self._expr[:self._expr.rfind(" ")] + f" {sym} "
        self._expr_var.set(self._expr)
        self.app.set_display(self._expr, self.app.get_result())

    def _clear(self):
        self._expr  = ""
        self._input = ""
        self._expr_var.set("")
        self.app.set_display("", "0")

    def _backspace(self):
        if self._input:
            self._input = self._input[:-1]
            self.app.set_display(self._expr + self._input, self._input or "0")
            self._expr_var.set(self._expr + self._input)

    def _negate(self):
        if self._input:
            if self._input.startswith("-"):
                self._input = self._input[1:]
            else:
                self._input = "-" + self._input
            self.app.set_display(self._expr + self._input, self._input)
            self._expr_var.set(self._expr + self._input)

    def _bracket(self, br: str):
        """Append a bracket character to the expression."""
        if self.app.get_result().startswith("Error"):
            self._clear()
        if br == "(":
            # If there's a pending input, treat it as implicit multiplication
            if self._input:
                self._expr += self._input + " * "
                self._input = ""
            self._expr += "("
        else:  # ")"
            if self._input:
                self._expr += self._input + ")"
                self._input = ""
            else:
                self._expr += ")"
        self._expr_var.set(self._expr + self._input)
        self.app.set_display(self._expr + self._input, self._input or "0")

    # ── Memory ───────────────────────────────────────────────────────────────

    def _ms(self):
        try:
            pc.memory_store(float(self.app.get_result()))
        except ValueError:
            pass

    def _mr(self):
        val = fmt(pc.memory_recall())
        self._input = val
        self.app.set_display(self._expr + val, val)
        self._expr_var.set(self._expr + val)

    def _mc(self):
        pc.memory_clear()

    def _mplus(self):
        try:
            pc.memory_add(float(self.app.get_result()))
        except ValueError:
            pass

    # ── Calculations (Command pattern) ───────────────────────────────────────

    def _equals(self):
        full_expr = (self._expr + self._input).strip()
        if not full_expr:
            return
        prev = self.app.get_result()

        def _do():
            # Replace display symbols with Python operators
            safe = full_expr.replace("×", "*").replace("÷", "/").replace("−", "-")
            return pc.evaluate(safe)

        cmd = CalcCommand(full_expr, _do, prev)
        try:
            result = cmd.execute()
            cmd_history.push(cmd)          # Command: push onto stack
            r_str = fmt(result)
            history_subject.notify(        # Observer: broadcast to all subscribers
                f"{full_expr} = {r_str}",
                full_expr,
                r_str,
            )
            self._expr  = ""
            self._input = r_str
            self._expr_var.set(full_expr + " =")
        except Exception as ex:
            self.app.set_display(full_expr, f"Error: {ex}")
            self._expr  = ""
            self._input = ""

    def _square(self):
        val = self._input or self.app.get_result()
        if not val or val.startswith("Error"):
            return
        prev = self.app.get_result()
        expr_str = f"({val})²"

        def _do():
            return pc.power(float(val), 2)

        cmd = CalcCommand(expr_str, _do, prev)
        try:
            result = cmd.execute()
            cmd_history.push(cmd)
            r_str = fmt(result)
            history_subject.notify(f"{expr_str} = {r_str}", expr_str, r_str)
            self._input = r_str
            self._expr  = ""
            self._expr_var.set(expr_str + " =")
        except Exception as ex:
            self.app.set_display(expr_str, f"Error: {ex}")

    def _sqrt(self):
        val = self._input or self.app.get_result()
        if not val or val.startswith("Error"):
            return
        prev = self.app.get_result()
        expr_str = f"√({val})"

        def _do():
            return pc.sqrt(float(val))

        cmd = CalcCommand(expr_str, _do, prev)
        try:
            result = cmd.execute()
            cmd_history.push(cmd)
            r_str = fmt(result)
            history_subject.notify(f"{expr_str} = {r_str}", expr_str, r_str)
            self._input = r_str
            self._expr  = ""
            self._expr_var.set(expr_str + " =")
        except Exception as ex:
            self.app.set_display(expr_str, f"Error: {ex}")

    def _undo(self):
        """Command pattern: pop the last command and restore previous value."""
        prev = cmd_history.undo()
        if prev is not None:
            self._input = str(prev)
            self._expr  = ""
            self._expr_var.set("(undo)")
            self.app.set_display("(undo)", str(prev))
        else:
            self.app.set_display("", "0")
            self._input = ""
            self._expr  = ""
            self._expr_var.set("")

    # ── Keyboard handler ─────────────────────────────────────────────────────

    def handle_key(self, event):
        k = event.keysym
        ch = event.char
        if ch in "0123456789":
            self._digit(ch)
        elif ch == ".":
            self._digit(".")
        elif ch in "+-":
            self._op(ch)
        elif ch == "*":
            self._op("*")
        elif ch == "/":
            self._op("/")
        elif ch == "%":
            self._op("%")
        elif ch == "(":
            self._bracket("(")
        elif ch == ")":
            self._bracket(")")
        elif k in ("Return", "KP_Enter"):
            self._equals()
        elif k == "Escape":
            self._clear()
        elif k == "BackSpace":
            self._backspace()



# =============================================================================
# SCIENTIFIC TAB  (created by ScientificTabFactory)
# =============================================================================

class ScientificTab:
    """
    Full scientific calculator tab.

    Deg/Rad mode behaviour:
    - DEG mode: sin/cos/tan accept degrees (converted to rad internally).
                asin/acos/atan return degrees (converted from rad internally).
    - RAD mode: all trig functions work directly in radians.
    - Hyperbolic functions (sinh/cosh/tanh) are NOT angle-based — mode ignored.
    - Constants, logs, powers, roots are also mode-independent.
    - "deg->rad" / "rad->deg" buttons convert the numeric value itself.
    """

    # Human-readable labels for history entries
    _LABELS = {
        "sin": "sin", "cos": "cos", "tan": "tan",
        "asin": "asin", "acos": "acos", "atan": "atan",
        "sinh": "sinh", "cosh": "cosh", "tanh": "tanh",
        "ln": "ln", "log10": "log₁₀", "log2": "log₂",
        "sq": "x²", "cu": "x³",
        "sqrt": "√x", "cbrt": "∛x",
        "exp": "exp", "fact": "n!",
        "recip": "1/x", "abs_": "|x|",
    }

    def __init__(self, parent, app):
        self.app = app
        parent.grid_columnconfigure(tuple(range(6)), weight=1)

        import tkinter as tk
        self._angle_mode = tk.StringVar(value="deg")

        # ── Top bar ──────────────────────────────────────────────────────────
        top = ctk.CTkFrame(parent, fg_color=theme_ctx.c("PANEL"), corner_radius=8)
        top.grid(row=0, column=0, columnspan=6, sticky="ew", padx=6, pady=(8, 4))
        top.grid_columnconfigure(2, weight=1)

        # Mode badge — updates text when toggle changes
        self._mode_label = ctk.CTkLabel(
            top, text="MODE: DEG",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=theme_ctx.c("ACCENT"),
            width=90,
        )
        self._mode_label.grid(row=0, column=0, padx=(10, 4), pady=6)

        # Segmented toggle
        self._seg = ctk.CTkSegmentedButton(
            top, values=["deg", "rad"],
            variable=self._angle_mode,
            command=self._on_mode_change,
            fg_color=theme_ctx.c("CARD"),
            selected_color=theme_ctx.c("ACCENT"),
            selected_hover_color=theme_ctx.c("HOVER_EQ"),
            unselected_color=theme_ctx.c("BTN_OP"),
            font=ctk.CTkFont(size=12, weight="bold"),
            height=32, width=120,
        )
        self._seg.grid(row=0, column=1, padx=(0, 8), pady=6)

        self._inp = ctk.CTkEntry(
            top, placeholder_text="Value  (blank = use display result)",
            fg_color=theme_ctx.c("CARD"), border_color=theme_ctx.c("ACCENT"),
            text_color=theme_ctx.c("TEXT"),
            font=ctk.CTkFont(size=13), height=32,
        )
        self._inp.grid(row=0, column=2, sticky="ew", padx=(0, 6), pady=6)

        ctk.CTkButton(
            top, text="← Use Result", width=110,
            fg_color=theme_ctx.c("BTN_SPEC"),
            hover_color=theme_ctx.c("HOVER_NUM"),
            text_color=theme_ctx.c("TEXT"),
            font=ctk.CTkFont(size=12),
            command=self._use_result,
        ).grid(row=0, column=3, padx=(0, 10), pady=6)

        # ── Button grid ──────────────────────────────────────────────────────
        # Row 1: Forward trig  (angle-sensitive)
        # Row 2: Inverse trig  (angle-sensitive) + hyperbolic (NOT angle-sensitive)
        # Row 3: Logs
        # Row 4: Powers + roots
        # Row 5: Constants + exp + factorial
        # Row 6: Combinatorics + utilities + angle converters

        btn_rows = [
            [("sin",     "sin",     "BTN_OP"),  ("cos",     "cos",     "BTN_OP"),  ("tan",     "tan",     "BTN_OP"),
             ("sinh",    "sinh",    "BTN_OP"),  ("cosh",    "cosh",    "BTN_OP"),  ("tanh",    "tanh",    "BTN_OP")],

            [("asin",    "asin",    "BTN_OP"),  ("acos",    "acos",    "BTN_OP"),  ("atan",    "atan",    "BTN_OP"),
             ("ln",      "ln",      "BTN_OP"),  ("log₁₀", "log10", "BTN_OP"),  ("log₂",  "log2",    "BTN_OP")],

            [("x²", "sq",      "BTN_OP"),  ("x³", "cu",      "BTN_OP"),  ("xⁿ", "xn",      "BTN_OP"),
             ("√x", "sqrt",    "BTN_OP"),  ("∛x", "cbrt",    "BTN_OP"),  ("ⁿ√x", "nrt", "BTN_OP")],

            [("π",  "pi",      "BTN_SPEC"), ("e",      "e_const", "BTN_SPEC"), ("τ", "tau",     "BTN_SPEC"),
             ("φ",  "phi",     "BTN_SPEC"), ("exp",    "exp",     "BTN_OP"),   ("n!",     "fact",    "BTN_OP")],

            [("C(n,r)",  "cnr",     "BTN_OP"),  ("P(n,r)", "pnr",     "BTN_OP"),  ("1/x",    "recip",   "BTN_OP"),
             ("|x|",     "abs_",    "BTN_OP"),  ("deg→rad", "d2r", "BTN_SPEC"), ("rad→deg", "r2d", "BTN_SPEC")],
        ]

        for r, row_btns in enumerate(btn_rows):
            for c, (label, key, color_key) in enumerate(row_btns):
                ctk.CTkButton(
                    parent, text=label,
                    command=lambda k=key: self._calc(k),
                    fg_color=theme_ctx.c(color_key),
                    hover_color=theme_ctx.c("HOVER_OP") if color_key == "BTN_OP" else theme_ctx.c("HOVER_NUM"),
                    text_color=theme_ctx.c("TEXT"),
                    font=ctk.CTkFont(size=13, weight="bold"),
                    corner_radius=8, height=46,
                ).grid(row=r + 1, column=c, padx=2, pady=2, sticky="nsew")

        for r in range(6):
            parent.grid_rowconfigure(r + 1, weight=1)

    # ── Mode toggle ──────────────────────────────────────────────────────────

    def _on_mode_change(self, value: str):
        """Called when the deg/rad segmented button is clicked."""
        self._mode_label.configure(
            text=f"MODE: {value.upper()}"
        )

    def _is_deg(self) -> bool:
        return self._angle_mode.get() == "deg"

    def _to_rad(self, v: float) -> float:
        """Input angle: convert degrees -> radians when in DEG mode."""
        return math.radians(v) if self._is_deg() else v

    def _from_rad(self, v: float) -> float:
        """Output angle: convert radians -> degrees when in DEG mode."""
        return math.degrees(v) if self._is_deg() else v

    # ── Value helpers ────────────────────────────────────────────────────────

    def _use_result(self):
        """Copy the current display result into the entry field."""
        val = self.app.get_result()
        if not val.startswith("Error"):
            self._inp.delete(0, "end")
            self._inp.insert(0, val)

    def _val(self) -> float:
        """Return numeric input: entry field if filled, else display result."""
        raw = self._inp.get().strip()
        if raw:
            return float(raw)
        display = self.app.get_result()
        if display and not display.startswith("Error"):
            return float(display)
        raise ValueError("No input — type a value or press \u2190 Use Result")

    def _push(self, label: str, result):
        r = fmt(result)
        history_subject.notify(f"{label} = {r}", label, r)
        cmd = CalcCommand(label, lambda res=result: res, self.app.get_result())
        cmd.result = result
        cmd_history.push(cmd)

    # ── Main dispatch ────────────────────────────────────────────────────────

    def _calc(self, key: str):
        try:
            # ── Constants (no input needed) ──────────────────────────────────
            if key == "pi":
                self._push("\u03c0", pc.PI);  return
            if key == "e_const":
                self._push("e", pc.E);         return
            if key == "tau":
                self._push("\u03c4", pc.TAU); return
            if key == "phi":
                self._push("\u03c6", pc.PHI); return

            # ── Angle converters (no trig, just unit conversion) ─────────────
            if key == "d2r":
                v = self._val()
                self._push(f"{v}\u00b0\u2192rad", math.radians(v)); return
            if key == "r2d":
                v = self._val()
                self._push(f"{v} rad\u2192\u00b0", math.degrees(v)); return

            # ── Dialog-based (need extra param) ─────────────────────────────
            if key == "xn":   self._power_n();   return
            if key == "nrt":  self._root_n();    return
            if key == "cnr":  self._combo_n_r(); return
            if key == "pnr":  self._perm_n_r();  return

            # ── All other ops need a numeric value ───────────────────────────
            v = self._val()
            mode = self._angle_mode.get().upper()

            # Trig: forward  — input is in current angle unit
            if key == "sin":
                result = pc.sin(self._to_rad(v))
                self._push(f"sin({v}{mode})", result); return
            if key == "cos":
                result = pc.cos(self._to_rad(v))
                self._push(f"cos({v}{mode})", result); return
            if key == "tan":
                result = pc.tan(self._to_rad(v))
                self._push(f"tan({v}{mode})", result); return

            # Trig: inverse — output is in current angle unit
            if key == "asin":
                result = self._from_rad(pc.asin(v))
                self._push(f"asin({v}) [{mode}]", result); return
            if key == "acos":
                result = self._from_rad(pc.acos(v))
                self._push(f"acos({v}) [{mode}]", result); return
            if key == "atan":
                result = self._from_rad(pc.atan(v))
                self._push(f"atan({v}) [{mode}]", result); return

            # Hyperbolic — NOT angle-sensitive
            if key == "sinh":
                self._push(f"sinh({v})", pc.sinh(v)); return
            if key == "cosh":
                self._push(f"cosh({v})", pc.cosh(v)); return
            if key == "tanh":
                self._push(f"tanh({v})", pc.tanh(v)); return

            # Logs
            if key == "ln":
                self._push(f"ln({v})", pc.log(v, math.e)); return
            if key == "log10":
                self._push(f"log\u2081\u2080({v})", pc.log10(v)); return
            if key == "log2":
                self._push(f"log\u2082({v})", pc.log2(v)); return

            # Powers
            if key == "sq":
                self._push(f"({v})\u00b2", pc.power(v, 2)); return
            if key == "cu":
                self._push(f"({v})\u00b3", pc.power(v, 3)); return

            # Roots
            if key == "sqrt":
                self._push(f"\u221a({v})", pc.sqrt(v)); return
            if key == "cbrt":
                self._push(f"\u221b({v})", pc.cbrt(v)); return

            # Other
            if key == "exp":
                self._push(f"exp({v})", pc.exp(v)); return
            if key == "fact":
                self._push(f"{int(v)}!", pc.factorial(int(v))); return
            if key == "recip":
                self._push(f"1/({v})", pc.divide(1, v)); return
            if key == "abs_":
                self._push(f"|{v}|", pc.absolute(v)); return

        except Exception as ex:
            self.app.set_display("Error", str(ex)[:60])

    # ── Dialog helpers ───────────────────────────────────────────────────────

    def _power_n(self):
        try:
            v = self._val()
        except Exception as ex:
            self.app.set_display("Error", str(ex)[:60]); return
        d = ctk.CTkInputDialog(text=f"Exponent n  (calculates {v}^n):", title="x\u207f")
        n = d.get_input()
        if n:
            try:
                self._push(f"({v})^{n}", pc.power(v, float(n)))
            except Exception as ex:
                self.app.set_display("Error", str(ex)[:60])

    def _root_n(self):
        try:
            v = self._val()
        except Exception as ex:
            self.app.set_display("Error", str(ex)[:60]); return
        d = ctk.CTkInputDialog(text=f"Root n  (calculates \u207f\u221a{v}):", title="\u207f\u221ax")
        n = d.get_input()
        if n:
            try:
                self._push(f"{n}\u221a({v})", pc.nth_root(v, float(n)))
            except Exception as ex:
                self.app.set_display("Error", str(ex)[:60])

    def _combo_n_r(self):
        d = ctk.CTkInputDialog(text="Enter n:", title="C(n,r)")
        n = d.get_input()
        if not n: return
        d2 = ctk.CTkInputDialog(text="Enter r:", title="C(n,r)")
        r = d2.get_input()
        if r:
            try:
                self._push(f"C({n},{r})", pc.combination(int(n), int(r)))
            except Exception as ex:
                self.app.set_display("Error", str(ex)[:60])

    def _perm_n_r(self):
        d = ctk.CTkInputDialog(text="Enter n:", title="P(n,r)")
        n = d.get_input()
        if not n: return
        d2 = ctk.CTkInputDialog(text="Enter r:", title="P(n,r)")
        r = d2.get_input()
        if r:
            try:
                self._push(f"P({n},{r})", pc.permutation(int(n), int(r)))
            except Exception as ex:
                self.app.set_display("Error", str(ex)[:60])


# =============================================================================
# STATISTICS TAB  (created by StatisticsTabFactory)
# =============================================================================

class StatisticsTab:
    def __init__(self, parent, app):
        self.app = app
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        scroll.grid_columnconfigure(0, weight=1)

        # Data input card
        dc = self._card(scroll, "Data Input", 0)
        dc.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(dc, text="Dataset (comma-separated):",
            font=ctk.CTkFont(size=12), text_color=theme_ctx.c("SUBTEXT"),
        ).grid(row=1, column=0, sticky="w", padx=10, pady=(4,2))
        self._data_e = ctk.CTkEntry(dc,
            placeholder_text="e.g. 1, 2, 3, 4, 5",
            fg_color=theme_ctx.c("CARD"), border_color=theme_ctx.c("ACCENT"),
            text_color=theme_ctx.c("TEXT"), font=ctk.CTkFont(size=13), height=34,
        )
        self._data_e.grid(row=2, column=0, sticky="ew", padx=10, pady=(0,10))

        # Stat buttons card
        sc = self._card(scroll, "Descriptive Statistics", 1)
        for c in range(4): sc.grid_columnconfigure(c, weight=1)
        ops = ["Mean","Median","Mode","Std Dev(s)","Std Dev(p)","Variance",
               "Range","Sum","Product","Geo Mean","Harm Mean"]
        for i, op in enumerate(ops):
            ctk.CTkButton(sc, text=op, command=lambda o=op: self._run(o),
                fg_color=theme_ctx.c("BTN_OP"), hover_color=theme_ctx.c("HOVER_OP"),
                text_color=theme_ctx.c("TEXT"), font=ctk.CTkFont(size=12,weight="bold"),
                corner_radius=8, height=38,
            ).grid(row=i//4+1, column=i%4, padx=3, pady=3, sticky="ew")

        # Percentile card
        pc2 = self._card(scroll, "Percentile", 2)
        pc2.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(pc2, text="p (0-100):", text_color=theme_ctx.c("SUBTEXT"),
            font=ctk.CTkFont(size=12)).grid(row=1,column=0,padx=(10,4),pady=8)
        self._p_e = ctk.CTkEntry(pc2, placeholder_text="75",
            fg_color=theme_ctx.c("CARD"), border_color=theme_ctx.c("ACCENT"),
            text_color=theme_ctx.c("TEXT"), height=30, width=80)
        self._p_e.grid(row=1,column=1,sticky="ew",padx=4,pady=8)
        ctk.CTkButton(pc2, text="Percentile", command=self._percentile,
            fg_color=theme_ctx.c("BTN_EQ"), hover_color=theme_ctx.c("HOVER_EQ"),
            text_color=theme_ctx.c("TEXT"), font=ctk.CTkFont(size=12,weight="bold"),
            height=30,
        ).grid(row=1,column=2,padx=(4,10),pady=8)

        # Correlation card
        cc = self._card(scroll, "Correlation", 3)
        cc.grid_columnconfigure(1, weight=1)
        for i,(lbl,attr) in enumerate([("X data:","_cx"),("Y data:","_cy")]):
            ctk.CTkLabel(cc, text=lbl, text_color=theme_ctx.c("SUBTEXT"),
                font=ctk.CTkFont(size=12)).grid(row=i+1,column=0,padx=(10,4),pady=4,sticky="w")
            e = ctk.CTkEntry(cc, placeholder_text="e.g. 1,2,3",
                fg_color=theme_ctx.c("CARD"), border_color=theme_ctx.c("ACCENT"),
                text_color=theme_ctx.c("TEXT"), height=30)
            e.grid(row=i+1,column=1,sticky="ew",padx=(4,10),pady=4)
            setattr(self, attr, e)
        ctk.CTkButton(cc, text="Correlation", command=self._corr,
            fg_color=theme_ctx.c("BTN_EQ"), hover_color=theme_ctx.c("HOVER_EQ"),
            text_color=theme_ctx.c("TEXT"), font=ctk.CTkFont(size=12,weight="bold"),
            height=30,
        ).grid(row=3,column=0,columnspan=2,padx=10,pady=(0,10),sticky="ew")

    def _card(self, parent, title, row):
        f = ctk.CTkFrame(parent, fg_color=theme_ctx.c("PANEL"), corner_radius=10)
        f.grid(row=row, column=0, sticky="ew", padx=4, pady=4)
        f.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(f, text=title, font=ctk.CTkFont(size=13,weight="bold"),
            text_color=theme_ctx.c("ACCENT"),
        ).grid(row=0,column=0,columnspan=4,sticky="w",padx=12,pady=(8,2))
        return f

    def _data(self):
        return [float(x.strip()) for x in self._data_e.get().split(",")]

    def _push(self, label, result):
        r = fmt(result)
        history_subject.notify(f"{label} = {r}", label, r)

    def _run(self, op):
        try:
            d = self._data()
            m = {"Mean":pc.mean,"Median":pc.median,"Mode":pc.mode,
                 "Std Dev(s)":lambda x:pc.std_dev(x,False),
                 "Std Dev(p)":lambda x:pc.std_dev(x,True),
                 "Variance":pc.variance,"Range":pc.data_range,
                 "Sum":pc.sum_data,"Product":pc.product_data,
                 "Geo Mean":pc.geometric_mean,"Harm Mean":pc.harmonic_mean}
            self._push(op, m[op](d))
        except Exception as ex:
            self.app.set_display("Error", str(ex)[:40])

    def _percentile(self):
        try:
            self._push(f"P{self._p_e.get()}", pc.percentile(self._data(), float(self._p_e.get())))
        except Exception as ex:
            self.app.set_display("Error", str(ex)[:40])

    def _corr(self):
        try:
            x = [float(v.strip()) for v in self._cx.get().split(",")]
            y = [float(v.strip()) for v in self._cy.get().split(",")]
            self._push("corr(x,y)", pc.correlation(x, y))
        except Exception as ex:
            self.app.set_display("Error", str(ex)[:40])


# =============================================================================
# FINANCIAL TAB  (created by FinancialTabFactory)
# =============================================================================

class FinancialTab:
    def __init__(self, parent, app):
        self.app = app
        parent.grid_columnconfigure((0,1), weight=1)
        parent.grid_rowconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)
        scroll.grid_columnconfigure((0,1), weight=1)

        def card(title, row, col, fields, btn, cb):
            f = ctk.CTkFrame(scroll, fg_color=theme_ctx.c("PANEL"), corner_radius=10)
            f.grid(row=row, column=col, sticky="nsew", padx=4, pady=4)
            f.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(f, text=title, font=ctk.CTkFont(size=13,weight="bold"),
                text_color=theme_ctx.c("ACCENT"),
            ).grid(row=0,column=0,columnspan=2,sticky="w",padx=12,pady=(8,4))
            entries = {}
            for i,(name,ph) in enumerate(fields):
                ctk.CTkLabel(f, text=name+":", text_color=theme_ctx.c("SUBTEXT"),
                    font=ctk.CTkFont(size=12)).grid(row=i+1,column=0,padx=(10,4),pady=3,sticky="w")
                e = ctk.CTkEntry(f, placeholder_text=ph,
                    fg_color=theme_ctx.c("CARD"), border_color=theme_ctx.c("ACCENT"),
                    text_color=theme_ctx.c("TEXT"), height=28)
                e.grid(row=i+1,column=1,sticky="ew",padx=(4,10),pady=3)
                entries[name] = e
            ctk.CTkButton(f, text=btn, command=lambda e=entries,c=cb: self._run(e,c),
                fg_color=theme_ctx.c("BTN_EQ"), hover_color=theme_ctx.c("HOVER_EQ"),
                text_color=theme_ctx.c("TEXT"), font=ctk.CTkFont(size=12,weight="bold"),
                height=30,
            ).grid(row=len(fields)+1,column=0,columnspan=2,padx=10,pady=(4,10),sticky="ew")

        def g(e,k): return float(e[k].get().strip())

        card("Simple Interest",0,0,
            [("Principal","1000"),("Rate","0.05"),("Time(yrs)","3")],
            "Calculate SI", lambda e: pc.simple_interest(g(e,"Principal"),g(e,"Rate"),g(e,"Time(yrs)")))
        card("Compound Interest",0,1,
            [("Principal","1000"),("Rate","0.05"),("n/yr","12"),("t(yrs)","3")],
            "Calculate CI", lambda e: pc.compound_interest(g(e,"Principal"),g(e,"Rate"),int(g(e,"n/yr")),g(e,"t(yrs)")))
        card("Present Value",1,0,
            [("Future Value","1500"),("Rate","0.05"),("Periods","10")],
            "Calculate PV", lambda e: pc.present_value(g(e,"Future Value"),g(e,"Rate"),int(g(e,"Periods"))))
        card("Future Value",1,1,
            [("Present Value","1000"),("Rate","0.05"),("Periods","10")],
            "Calculate FV", lambda e: pc.future_value(g(e,"Present Value"),g(e,"Rate"),int(g(e,"Periods"))))
        card("Loan Payment",2,0,
            [("Principal","200000"),("Annual Rate","0.06"),("Years","30")],
            "Calculate PMT", lambda e: pc.loan_payment(g(e,"Principal"),g(e,"Annual Rate"),int(g(e,"Years"))))
        card("ROI",2,1,
            [("Gain","1500"),("Cost","1000")],
            "Calculate ROI%", lambda e: pc.roi(g(e,"Gain"),g(e,"Cost")))
        card("Break-Even",3,0,
            [("Fixed Costs","5000"),("Price/Unit","25"),("Var Cost/Unit","10")],
            "Calculate BEP", lambda e: pc.break_even(g(e,"Fixed Costs"),g(e,"Price/Unit"),g(e,"Var Cost/Unit")))
        card("Inflation Adjusted",3,1,
            [("Amount","1000"),("Inflation Rate","0.03"),("Years","10")],
            "Calculate Adj", lambda e: pc.inflation_adjusted(g(e,"Amount"),g(e,"Inflation Rate"),int(g(e,"Years"))))

    def _run(self, entries, cb):
        try:
            result = cb(entries)
            r = fmt(result)
            history_subject.notify(f"Financial = {r}", "Financial", r)
        except Exception as ex:
            self.app.set_display("Error", str(ex)[:40])


# =============================================================================
# MATRIX TAB  (created by MatrixTabFactory)
# =============================================================================

class MatrixTab:
    def __init__(self, parent, app):
        self.app = app
        import tkinter as tk
        parent.grid_columnconfigure((0,1), weight=1)
        parent.grid_rowconfigure(1, weight=1)

        # Size selector
        top = ctk.CTkFrame(parent, fg_color="transparent", height=40)
        top.grid(row=0, column=0, columnspan=2, sticky="ew", padx=8, pady=(8,4))
        top.grid_propagate(False)
        ctk.CTkLabel(top, text="Size:", text_color=theme_ctx.c("SUBTEXT"),
            font=ctk.CTkFont(size=13)).pack(side="left", padx=(4,8))
        self._size = tk.IntVar(value=3)
        for sz in (2,3,4):
            ctk.CTkRadioButton(top, text=f"{sz}x{sz}", variable=self._size, value=sz,
                command=self._rebuild, fg_color=theme_ctx.c("ACCENT"),
                hover_color=theme_ctx.c("HOVER_EQ"), font=ctk.CTkFont(size=12),
            ).pack(side="left", padx=6)

        # Matrix A frame
        self._fa = ctk.CTkFrame(parent, fg_color=theme_ctx.c("PANEL"), corner_radius=10)
        self._fa.grid(row=1, column=0, sticky="nsew", padx=(8,4), pady=4)
        ctk.CTkLabel(self._fa, text="Matrix A", font=ctk.CTkFont(size=13,weight="bold"),
            text_color=theme_ctx.c("ACCENT")).grid(row=0,column=0,columnspan=4,pady=(8,4))
        self._ia = ctk.CTkFrame(self._fa, fg_color="transparent")
        self._ia.grid(row=1, column=0, padx=10, pady=(0,8))

        # Matrix B frame
        self._fb = ctk.CTkFrame(parent, fg_color=theme_ctx.c("PANEL"), corner_radius=10)
        self._fb.grid(row=1, column=1, sticky="nsew", padx=(4,8), pady=4)
        ctk.CTkLabel(self._fb, text="Matrix B", font=ctk.CTkFont(size=13,weight="bold"),
            text_color=theme_ctx.c("ACCENT")).grid(row=0,column=0,columnspan=4,pady=(8,4))
        self._ib = ctk.CTkFrame(self._fb, fg_color="transparent")
        self._ib.grid(row=1, column=0, padx=10, pady=(0,8))

        # Operations
        ops_f = ctk.CTkFrame(parent, fg_color=theme_ctx.c("PANEL"), corner_radius=10)
        ops_f.grid(row=2, column=0, columnspan=2, sticky="ew", padx=8, pady=4)
        for c in range(5): ops_f.grid_columnconfigure(c, weight=1)
        ctk.CTkLabel(ops_f, text="Operations", font=ctk.CTkFont(size=13,weight="bold"),
            text_color=theme_ctx.c("ACCENT")).grid(row=0,column=0,columnspan=5,pady=(8,4))
        for c,(lbl,op) in enumerate([("A+B","add"),("A-B","sub"),("AxB","mul"),("Scalar","scalar"),("Transpose","trans")]):
            ctk.CTkButton(ops_f, text=lbl, command=lambda o=op: self._op(o),
                fg_color=theme_ctx.c("BTN_OP"), hover_color=theme_ctx.c("HOVER_OP"),
                text_color=theme_ctx.c("TEXT"), font=ctk.CTkFont(size=12,weight="bold"),
                corner_radius=8, height=36,
            ).grid(row=1,column=c,padx=3,pady=4,sticky="ew")
        for c,(lbl,op) in enumerate([("det(A)","det"),("trace(A)","trace"),("Identity","ident"),("Clear A","clrA"),("Clear B","clrB")]):
            ctk.CTkButton(ops_f, text=lbl, command=lambda o=op: self._op(o),
                fg_color=theme_ctx.c("BTN_SPEC"), hover_color=theme_ctx.c("HOVER_NUM"),
                text_color=theme_ctx.c("TEXT"), font=ctk.CTkFont(size=12,weight="bold"),
                corner_radius=8, height=36,
            ).grid(row=2,column=c,padx=3,pady=(0,8),sticky="ew")

        # Output
        out_f = ctk.CTkFrame(parent, fg_color=theme_ctx.c("PANEL"), corner_radius=10)
        out_f.grid(row=3, column=0, columnspan=2, sticky="ew", padx=8, pady=(0,8))
        out_f.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(out_f, text="Result", font=ctk.CTkFont(size=13,weight="bold"),
            text_color=theme_ctx.c("ACCENT")).grid(row=0,column=0,sticky="w",padx=12,pady=(8,2))
        self._out = ctk.CTkTextbox(out_f, height=90,
            font=ctk.CTkFont(family="Consolas",size=13),
            fg_color=theme_ctx.c("CARD"), text_color=theme_ctx.c("TEXT"),
            border_color=theme_ctx.c("ACCENT"), border_width=1, state="disabled")
        self._out.grid(row=1,column=0,sticky="ew",padx=10,pady=(0,10))

        self._ea, self._eb = [], []
        self._rebuild()

    def _rebuild(self):
        n = self._size.get()
        for w in self._ia.winfo_children(): w.destroy()
        for w in self._ib.winfo_children(): w.destroy()
        self._ea = self._grid(self._ia, n)
        self._eb = self._grid(self._ib, n)

    def _grid(self, parent, n):
        rows = []
        for r in range(n):
            row = []
            for c in range(n):
                e = ctk.CTkEntry(parent, width=56, height=34,
                    font=ctk.CTkFont(family="Consolas",size=13),
                    fg_color=theme_ctx.c("CARD"), border_color=theme_ctx.c("BTN_OP"),
                    text_color=theme_ctx.c("TEXT"), justify="center")
                e.grid(row=r, column=c, padx=2, pady=2)
                e.insert(0,"0")
                row.append(e)
            rows.append(row)
        return rows

    def _read(self, entries):
        return [[float(entries[r][c].get() or "0") for c in range(len(entries[r]))] for r in range(len(entries))]

    def _show(self, result, label):
        r = fmt(result)
        self._out.configure(state="normal")
        self._out.delete("1.0","end")
        self._out.insert("1.0", r)
        self._out.configure(state="disabled")
        disp = r[:40] if not isinstance(result,list) else "Matrix result"
        history_subject.notify(f"{label} = {r[:60]}", label, disp)

    def _op(self, op):
        try:
            A = self._read(self._ea)
            if op == "add":    self._show(pc.matrix.add(A, self._read(self._eb)), "A+B")
            elif op == "sub":  self._show(pc.matrix.subtract(A, self._read(self._eb)), "A-B")
            elif op == "mul":  self._show(pc.matrix.multiply(A, self._read(self._eb)), "AxB")
            elif op == "trans":self._show(pc.matrix.transpose(A), "Transpose(A)")
            elif op == "det":  self._show(pc.matrix.determinant(A), "det(A)")
            elif op == "trace":self._show(pc.matrix.trace(A), "trace(A)")
            elif op == "scalar":
                d = ctk.CTkInputDialog(text="Enter scalar:", title="Scalar")
                k = d.get_input()
                if k: self._show(pc.matrix.scalar_multiply(A, float(k)), f"{k}xA")
            elif op == "ident":
                d = ctk.CTkInputDialog(text="Enter size n:", title="Identity")
                n = d.get_input()
                if n: self._show(pc.matrix.identity(int(n)), f"I({n})")
            elif op == "clrA":
                for row in self._ea:
                    for e in row: e.delete(0,"end"); e.insert(0,"0")
            elif op == "clrB":
                for row in self._eb:
                    for e in row: e.delete(0,"end"); e.insert(0,"0")
        except Exception as ex:
            self.app.set_display("Error", str(ex)[:40])


# =============================================================================
# ENTRY POINT
# =============================================================================

def main():
    app = CalculatorApp()
    app.mainloop()

if __name__ == "__main__":
    main()
