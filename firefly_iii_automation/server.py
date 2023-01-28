import json
import logging
from functools import lru_cache
from io import StringIO

import firefly_iii_client
from simple_websocket_server import WebSocket, WebSocketServer

from firefly_iii_automation.firefly import get_all_asset_accounts, find_transaction_by_external_id, \
    create_new_transaction
from firefly_iii_automation.models import FireflyTransaction, FireflyTransactionTypes
from firefly_iii_automation.transactions_parsers import parse_bt_transaction_report
from firefly_iii_automation.utils.json import dumps

logger = logging.getLogger(__name__)


class SimpleWebSocketServer(WebSocket):
    def handle(self):
        data = json.loads(self.data)

        if 'content' in data:
            self.parse_transactions(data['content'])

        if 'transaction' in data:
            self.insert_to_firefly(data['transaction'])

    def insert_to_firefly(self, transaction: dict):
        try:
            transaction = FireflyTransaction.from_dict(transaction)
            create_new_transaction(transaction)
            message = f"Transaction with external id {transaction.external_id} successfully inserted"
            logger.info(message)
            self.send_json_message({'info': message})
        except firefly_iii_client.exceptions.ApiException:
            message = 'Failed to insert transaction!'
            logger.error(message)
            self.send_json_message({'error': message})
        except Exception as ex:
            message = str(ex)
            logger.exception(ex)
            self.send_json_message({'error': message})

    def parse_transactions(self, content):
        try:
            file_obj = StringIO(content)
            transactions = []
            for transaction in parse_bt_transaction_report(file_obj):
                if transaction.type in (FireflyTransactionTypes.WITHDRAWAL, FireflyTransactionTypes.TRANSFER):
                    account = self.get_assets_accounts().get(transaction.source_account)
                    if account:
                        transaction.source_account = account['attributes']['name']
                    else:
                        transaction.source_account = '!!UNKNOWN!!'

                elif transaction.type is FireflyTransactionTypes.DEPOSIT:
                    account = self.get_assets_accounts().get(transaction.destination_account)
                    if account:
                        transaction.destination_account = account['attributes']['name']
                    else:
                        transaction.destination_account = '!!UNKNOWN!!'

                message = f'Checking if transaction with external id exists:\t{transaction.external_id}'
                logger.info(message)
                self.send_json_message({'info': message})
                existing_transaction = find_transaction_by_external_id(transaction.external_id)

                if existing_transaction:
                    logger.info(f"Transaction with external id {transaction.external_id} already exists!")
                else:
                    transactions.append(transaction.to_dict())
                    message = f"Transaction with external id {transaction.external_id} doesn't exist"
                    logger.info(message)
                    self.send_json_message({'info': message})

            self.send_json_message({"transactions": transactions})
        except Exception as ex:
            message = str(ex)
            logger.exception(ex)
            self.send_json_message({'error': message})

    @lru_cache()
    def get_assets_accounts(self):
        return {
            account['attributes'].get('iban') or account['attributes'].get('name'): account
            for account in get_all_asset_accounts()
        }

    def connected(self):
        print(self.address, 'connected')

    def handle_close(self):
        print(self.address, 'closed')

    def send_json_message(self, message):
        self.send_message(dumps(message))


server = WebSocketServer('', 8000, SimpleWebSocketServer)

if __name__ == "__main__":
    server = WebSocketServer('', 8000, SimpleWebSocketServer)
    server.serve_forever()
