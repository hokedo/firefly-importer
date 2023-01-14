#!/usr/bin/env python
from pathlib import Path

import typer

from automation.firefly import get_all_transactions
from automation.transactions_parsers import parse_bt_transaction_report

app = typer.Typer()


@app.command()
def parse_bt_report(path: Path):
    get_all_transactions()
    # parse_bt_transaction_report(path)


if __name__ == "__main__":
    app()
