#!/usr/bin/env python
import logging
from pathlib import Path

import typer

from firefly_iii_automation.exceptions import NoMatchingAccount
from firefly_iii_automation.firefly import get_all_asset_accounts, create_new_transaction, \
    find_transaction_by_external_id
from firefly_iii_automation.transactions_parsers import parse_bt_transaction_report

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = typer.Typer()

logger = logging.getLogger(__name__)


def parse_bt_report(path: Path):
    accounts = {
        account['attributes'].get('iban') or account['attributes'].get('name'): account
        for account in get_all_asset_accounts()
    }
    transactions = parse_bt_transaction_report(path)

    for transaction in transactions:
        account = accounts.get(transaction.source_account)

        if not account:
            raise NoMatchingAccount(
                f"No matching account '{transaction.source_account}' exists in Firefly for transaction "
                f"external id {transaction.external_id}"
            )
        else:
            transaction.source_account = account['attributes']['name']

        logger.info(f'Checking if transaction with external id exists:\t{transaction.external_id}')
        existing_transaction = find_transaction_by_external_id(transaction.external_id)

        if existing_transaction:
            logger.info(f"Transaction with external id {transaction.external_id} already exists!")
        else:
            logger.info(f"Transaction with external id {transaction.external_id} doesn't exist")
            create_new_transaction(transaction)
            logger.info(f"Transaction with external id {transaction.external_id} successfully inserted")


if __name__ == "__main__":
    # app()
    app = FireflyTransactionsApp()
    app.run()
