from functools import lru_cache

import firefly_iii_client
from firefly_iii_client.api.transactions_api import TransactionsApi

from .env import FIREFLY_III_ACCESS_TOKEN, FIREFLY_III_HOST


@lru_cache()
def create_configuration():
    return firefly_iii_client.Configuration(
        host=FIREFLY_III_HOST,
        access_token=FIREFLY_III_ACCESS_TOKEN
    )


@lru_cache()
def create_api_client():
    configuration = create_configuration()
    return firefly_iii_client.ApiClient(configuration)


def get_all_transactions():
    with create_api_client() as api_client:
        transactions_api = TransactionsApi(api_client)

        t = transactions_api.list_transaction()
        print(t)
