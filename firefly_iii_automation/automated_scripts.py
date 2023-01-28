import logging
from pathlib import Path

from firefly_iii_automation.exceptions import NoMatchingAccount
from firefly_iii_automation.firefly import get_all_asset_accounts, find_transaction_by_external_id, \
    create_new_transaction
from firefly_iii_automation.transactions_parsers import parse_bt_transaction_report

logger = logging.getLogger(__name__)


def parse_bt_report(path: Path):
    accounts = {
        account['attributes'].get('iban') or account['attributes'].get('name'): account
        for account in get_all_asset_accounts()
    }

    with path.open() as f:
        transactions = parse_bt_transaction_report(f)

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
