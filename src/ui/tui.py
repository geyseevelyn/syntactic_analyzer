import os
from io import StringIO
from contextlib import redirect_stdout

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, DirectoryTree, TabbedContent, TabPane, RichLog, Static
from textual import on

# Imports reusing the existing analysis pipeline and report printers
from ..lexical.lexer import analyze_text
from ..lexical.reports import show_tokens, show_symbol_table, show_token_count
from ..parsing.grammar import parse_text
from ..parsing.reports import show_syntax_summary, show_syntax_errors


def _capture(func, *args, **kwargs) -> str:
    """Capture stdout from existing report functions as a string."""
    buf = StringIO()
    with redirect_stdout(buf):
        func(*args, **kwargs)
    return buf.getvalue()


class AnalyzerTUI(App):
    CSS = """
    Screen {
        layout: horizontal;
    }
    # Left pane (file explorer)
    # Right pane (tabs)
    # Provide a sensible minimum width to explorer
    # and let tabs take the remaining space
    # using fractions
    .left {
        width: 1fr;
        min-width: 1fr;
        border: round $accent;
    }
    .right {
        width: 3fr;
        border: round $accent;
    }
    .hint {
        color: $text-muted;
    }
    #explorer {
        width: 1fr;
        min-width: 1fr;
        border: round red;
        padding: 1;
    }
    """

    BINDINGS = [
        ("q", "quit", "Sair"),
        ("r", "recarregar", "Recarregar arquivo"),
    ]

    def __init__(self, start_dir: str | None = None) -> None:
        super().__init__()
        self.start_dir = start_dir or self._default_root()
        self.current_file: str | None = None
        # Cache of last analysis data
        self._lex_data = None  # (processed_tokens, symbol_table, error_tokens)
        self._summary = None
        self._syntax_errors = None

    def _default_root(self) -> str:
        # Project root = three levels up from this file
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            with Vertical(classes="left"):
                yield Static("Explorador de Arquivos (selecione um .tonto)", classes="hint")
                yield DirectoryTree(self.start_dir, id="tree")
            with Vertical(classes="right"):
                with TabbedContent(id="tabs"):
                    with TabPane("Tokens"):
                        yield RichLog(id="tab_tokens", wrap=True, highlight=True)
                    with TabPane("Tabela de Símbolos"):
                        yield RichLog(id="tab_symtab", wrap=True, highlight=True)
                    with TabPane("Contagem de Tokens"):
                        yield RichLog(id="tab_tokcount", wrap=True, highlight=True)
                    with TabPane("Resumo Sintático"):
                        yield RichLog(id="tab_summary", wrap=True, highlight=True)
                    with TabPane("Erros Sintáticos"):
                        yield RichLog(id="tab_syserrs", wrap=True, highlight=True)
        yield Footer()

    def action_recarregar(self) -> None:
        if self.current_file:
            self._run_all(self.current_file)

    @on(DirectoryTree.FileSelected)
    def handle_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        pstr = str(event.path)
        if not pstr.lower().endswith(".tonto"):
            self.notify("Só é possível analisar arquivos com extensão .tonto", severity="warning")
            return
        self.current_file = pstr
        self._run_all(pstr)

    def _set_tab_text(self, widget_id: str, text: str) -> None:
        widget = self.query_one(f"#{widget_id}", RichLog)
        widget.clear()
        # Split for incremental append to keep log performant
        for line in text.splitlines():
            widget.write(line)

    def _run_all(self, file_path: str) -> None:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = f.read()
        except OSError as e:
            self.notify(f"Erro ao abrir arquivo: {e}", severity="error")
            return

        # 1) Lexical analysis
        processed_tokens, symbol_table, error_tokens = analyze_text(data)
        self._lex_data = (processed_tokens, symbol_table, error_tokens)

        # 2) Syntactic analysis
        ast, summary, errors = parse_text(data)
        self._summary = summary
        self._syntax_errors = errors

        # Render into tabs using the existing report functions (captured)
        tokens_txt = _capture(show_tokens, processed_tokens, error_tokens)
        symtab_txt = _capture(show_symbol_table, symbol_table)
        count_txt = _capture(show_token_count, processed_tokens)
        summary_txt = _capture(show_syntax_summary, summary) if summary is not None else "Nenhuma análise realizada."
        syserrs_txt = _capture(show_syntax_errors, errors) if errors is not None else "Nenhuma análise realizada."

        self._set_tab_text("tab_tokens", tokens_txt)
        self._set_tab_text("tab_symtab", symtab_txt)
        self._set_tab_text("tab_tokcount", count_txt)
        self._set_tab_text("tab_summary", summary_txt)
        self._set_tab_text("tab_syserrs", syserrs_txt)

        # Notify status
        if errors:
            self.notify(f"Análise concluída com {len(errors)} erro(s) sintático(s).", severity="warning")
        else:
            self.notify("Análise sintática concluída com sucesso!", severity="information")


def main() -> None:
    # Prefer opening examples directory if it exists
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    examples_dir = os.path.join(project_root, "examples")
    start_dir = examples_dir if os.path.isdir(examples_dir) else project_root
    app = AnalyzerTUI(start_dir=start_dir)
    app.run()


if __name__ == "__main__":
    main()
