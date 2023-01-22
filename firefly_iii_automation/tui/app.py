from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Label, Input, Static
from textual_autocomplete import AutoComplete, Dropdown, DropdownItem


def compose_currency_dropdown(id=None):
    return AutoComplete(
        Input(value="RON"),
        Dropdown(items=[
            DropdownItem("RON"),
            DropdownItem("EUR"),
        ]),
        id=id
    )


def compose_category_dropdown():
    return AutoComplete(
        Input(value="Food"),
        Dropdown(items=[
            DropdownItem("Food"),
            DropdownItem("Cheltuieli"),
        ]),
        id="category"
    )


class TransactionForm(Static):
    def compose(self) -> ComposeResult:
        yield Label("Date")
        yield Input(value="23-01-2023")

        yield Label("Description")
        yield Input(value="Mancare comandata")

        yield Label("Source account")
        yield Input(value="Banca Transilvania - Card Credit")

        yield Label("Destination account")
        yield Input(value="Tazz")

        yield Label("Amount")
        yield Input(value="135")

        yield Label("Currency")
        yield compose_currency_dropdown(id="currency")

        yield Horizontal(
            Container(
                Label("Foreign Amount"),
                Input(value="50"),
            ),
            Container(
                Label("Foreign Currency"),
                compose_currency_dropdown(id="foreign_currency"),
            ), id="foreign-amount",
        )

        yield Label("Category")
        yield compose_category_dropdown()


class FireflyTransactionsApp(App):
    """A Textual app to manage storing firefly transactions."""

    CSS_PATH = "css/app.css"

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield Container(TransactionForm(expand=True))

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark


if __name__ == "__main__":
    app = FireflyTransactionsApp()
    app.run()
