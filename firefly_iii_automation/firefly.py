import logging
from functools import lru_cache

import firefly_iii_client
from firefly_iii_client.api.accounts_api import AccountsApi
from firefly_iii_client.api.autocomplete_api import AutocompleteApi
from firefly_iii_client.api.categories_api import CategoriesApi
from firefly_iii_client.api.search_api import SearchApi
from firefly_iii_client.api.transactions_api import TransactionsApi

from .env import FIREFLY_III_ACCESS_TOKEN, FIREFLY_III_HOST
from .models import FireflyTransaction
from .utils.json import dumps

logger = logging.getLogger(__name__)


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


def get_all_accounts():
    logger.info("Fetching all accounts page 1")
    with create_api_client() as api_client:
        accounts_api = AccountsApi(api_client)
        response = accounts_api.list_account()

        for entry in response['data']:
            yield entry

        current_page = 1
        total_pages = response['meta']['pagination']['total_pages']
        while current_page < total_pages:
            current_page += 1
            logger.info(f"Fetching all accounts page {current_page}")
            response = accounts_api.list_account(page=current_page)
            for entry in response['data']:
                yield entry


def get_all_categories():
    logger.info("Fetching all categories page 1")
    with create_api_client() as api_client:
        categories_api = CategoriesApi(api_client)
        response = categories_api.list_category()

        for entry in response['data']:
            yield entry

        current_page = 1
        total_pages = response['meta']['pagination']['total_pages']
        while current_page < total_pages:
            current_page += 1
            logger.info(f"Fetching all categories page {current_page}")
            response = categories_api.list_category(page=current_page)
            for entry in response['data']:
                yield entry


def get_all_asset_accounts():
    logger.info("Fetching all asset accounts page 1")
    with create_api_client() as api_client:
        accounts_api = AccountsApi(api_client)
        response = accounts_api.list_account(type='asset')

        for entry in response['data']:
            yield entry

        current_page = 1
        total_pages = response['meta']['pagination']['total_pages']
        while current_page < total_pages:
            current_page += 1
            logger.info(f"Fetching all asset accounts page {current_page}")
            response = accounts_api.list_account(page=current_page, type='asset')
            for entry in response['data']:
                yield entry


def get_all_descriptions():
    logger.info("Fetching all descriptions")
    with create_api_client() as api_client:
        autocomplete_api = AutocompleteApi(api_client)
        response = autocomplete_api.get_transactions_ac(limit=99999)
        for entry in response.value:
            yield entry


def create_new_transaction(transaction: FireflyTransaction):
    logger.info(f"Inserting transaction with external id:\t{transaction.external_id}")
    with create_api_client() as api_client:
        transactions_api = TransactionsApi(api_client)
        try:
            response = transactions_api.store_transaction(transaction.to_transaction_store())
            logger.info(f"Insertion response for external id {dumps(response['data'].to_dict())}")
        except firefly_iii_client.exceptions.ApiException as ex:
            logger.error(
                f"Failed insertion of transaction with external id "
                f"'{transaction.external_id}':\t{ex.body}\t{dumps(transaction.to_dict())}"
            )
            raise ex


def find_transaction_by_external_id(external_id):
    with create_api_client() as api_client:
        search_api = SearchApi(api_client)
        response = search_api.search_transactions(f"external_id_is:{external_id}")

        if response['data']:
            return response['data'][0]
