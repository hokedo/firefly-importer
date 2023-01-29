import logging

from asyncer import asyncify

from .sync import (
    create_configuration as sync_create_configuration,
    create_new_transaction as sync_create_new_transaction,
    create_api_client as sync_create_api_client,
    get_all_accounts as sync_get_all_accounts,
    get_all_categories as sync_get_all_categories,
    get_all_descriptions as sync_get_all_descriptions,
    get_all_asset_accounts as sync_get_all_asset_accounts,
    find_transaction_by_external_id as sync_find_transaction_by_external_id
)
from ..models import FireflyTransaction

logger = logging.getLogger(__name__)


async def create_configuration():
    return await asyncify(sync_create_configuration)()


async def create_api_client():
    return await asyncify(sync_create_api_client)()


async def get_all_accounts():
    for item in await asyncify(sync_get_all_accounts)():
        yield item


async def get_all_categories():
    for item in await asyncify(sync_get_all_categories)():
        yield item


async def get_all_asset_accounts():
    for item in await asyncify(sync_get_all_asset_accounts)():
        yield item


async def get_all_descriptions():
    for item in await asyncify(sync_get_all_descriptions)():
        yield item


async def create_new_transaction(transaction: FireflyTransaction):
    return await asyncify(sync_create_new_transaction)(transaction)


async def find_transaction_by_external_id(external_id):
    return await asyncify(sync_find_transaction_by_external_id)(external_id)
