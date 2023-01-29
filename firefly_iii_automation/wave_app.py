import asyncio
import logging
from typing import AsyncIterator

from aiocache import cached
from aiofiles.tempfile import _temporary_directory
from aiopath import AsyncPath
from anyio import create_memory_object_stream
from anyio.streams.memory import MemoryObjectSendStream
# noinspection PyUnresolvedReferences
from h2o_wave import Q, main, app, ui

from firefly_iii_automation.firefly._async import get_all_accounts, get_all_categories, \
    get_all_descriptions as _get_all_descriptions, get_all_asset_accounts, find_transaction_by_external_id
from firefly_iii_automation.models import FireflyTransactionTypes, FireflyTransaction
from firefly_iii_automation.transactions_parsers import parse_bt_transaction_report

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

CURRENCIES = ['RON', 'EUR']


@app('/')
async def serve(q: Q):
    form_items = []

    if q.args.file_upload or q.client.transactions:
        if q.client.current_file is None:
            # File was uploaded just now
            q.client_temp_dir = await _temporary_directory()
            q.client.current_file = await q.site.download(q.args.file_upload[0], q.client_temp_dir.name)
            await q.site.unload(q.args.file_upload[0])

            q.client.transactions = parse_transactions(q.client.current_file)

            accounts, categories, descriptions = await asyncio.gather(
                get_all_accounts_names(),
                get_all_categories_names(),
                get_all_descriptions(),
            )
            q.client.accounts = accounts
            q.client.categories = categories
            q.client.descriptions = descriptions

        # Get the next transaction to show
        q.client.current_transaction = await anext(q.client.transactions)

        # Hide the file upload input and show the transaction fields
        form_items += await build_form_transaction_fields(q)
    else:
        # Only show the file upload input
        form_items += [ui.file_upload(name='file_upload', label='File Upload', multiple=False, compact=True)]

    form_items += [
        ui.buttons(
            justify='center',
            items=[ui.button(name='submit_button', label='Submit', width='100%', primary=True)]
        )
    ]

    q.page['form'] = ui.form_card(box='4 1 6 12', items=form_items)
    await q.page.save()


async def build_form_transaction_fields(q):
    current_transaction = q.client.current_transaction  # type: FireflyTransaction
    return [
        ui.inline(items=[
            ui.combobox(name='type', label='Type', choices=['Withdrawal', 'Deposit', 'Transfer'], width='25%',
                        required=True, value=current_transaction.type.value.capitalize()),
            ui.combobox(name='description', label='Description', choices=q.client.descriptions, width='75%',
                        required=True),
        ]),
        ui.inline(items=[
            ui.combobox(name='source_account', label='Source Account',
                        choices=q.client.accounts, value=current_transaction.source_account,
                        width='50%', required=True),
            ui.combobox(name='destination_account', label='Destination Account',
                        choices=q.client.accounts, value=current_transaction.destination_account,
                        width='50%', required=True),
        ]),
        ui.inline(items=[
            ui.date_picker(name='date', label='Date', value=current_transaction.date.isoformat(), width="50%"),
            ui.combobox(name='category_name', label='Category Name',
                        choices=q.client.categories, value=current_transaction.category_name,
                        width="50%")
        ]),
        ui.inline(items=[
            ui.textbox(name='amount', label='Amount', width="50%", mask='99.99', value=str(current_transaction.amount),
                       required=True),
            ui.combobox(name='currency_code', label='Currency',
                        choices=CURRENCIES, width="50%", value=current_transaction.currency_code)
        ]),
        ui.inline(items=[
            ui.textbox(name='foreign_amount', label='Foreign Amount',
                       value=str(current_transaction.foreign_amount or ''), width="50%", mask='99.99'),
            ui.combobox(name='foreign_currency_code', label='Foreign Currency',
                        choices=CURRENCIES, value=current_transaction.foreign_currency_code, width="50%")
        ]),
        ui.textbox(name='notes', label='notes', width="100%", multiline=True, value=current_transaction.notes),
    ]


@cached()
async def get_all_accounts_names():
    return sorted({account['attributes']['name'] async for account in get_all_accounts()})


@cached()
async def get_assets_accounts():
    return {
        account['attributes'].get('iban') or account['attributes'].get('name'): account
        async for account in get_all_asset_accounts()
    }


@cached()
async def get_all_categories_names():
    return sorted({category['attributes']['name'] async for category in get_all_categories()})


@cached()
async def get_all_descriptions():
    return sorted({description['name'] async for description in _get_all_descriptions()})


async def parse_transactions(file_location: str) -> AsyncIterator[FireflyTransaction]:
    """
    Asynchronously read the file and start yielding parsed transactions in a separate thread
    The parsed transactions will be buffered in send_stream. receive_stream will start reading
    only when the next value is needed out of this generator. This means that the send_stream
    will continuously receive transactions in the background but this generator will only start
    return one when needed. This means that this generator will wait for the first transaction
    to be parsed and put into the send_stream and then return it.
    :param file_location:
    :return:
    """
    send_stream, receive_stream = create_memory_object_stream(max_buffer_size=1000, item_type=FireflyTransaction)

    # Run parsing task in the background without blocking the current thread
    asyncio.create_task(filter_existing_transactions(file_location, send_stream))

    async with receive_stream:
        async for transaction in receive_stream:
            yield transaction


async def filter_existing_transactions(file_location: str, send_stream: MemoryObjectSendStream):
    file_location = AsyncPath(file_location)
    async with file_location.open() as f:
        async for transaction in parse_bt_transaction_report(f):
            assets_accounts = await get_assets_accounts()
            if transaction.type in (FireflyTransactionTypes.WITHDRAWAL, FireflyTransactionTypes.TRANSFER):
                account = assets_accounts.get(transaction.source_account)
                if account:
                    transaction.source_account = account['attributes']['name']
                else:
                    transaction.source_account = '!!UNKNOWN!!'

            elif transaction.type is FireflyTransactionTypes.DEPOSIT:
                account = assets_accounts.get(transaction.destination_account)
                if account:
                    transaction.destination_account = account['attributes']['name']
                else:
                    transaction.destination_account = '!!UNKNOWN!!'
            logger.info(f'Checking if transaction with external id exists:\t{transaction.external_id}')
            existing_transaction = await find_transaction_by_external_id(transaction.external_id)
            if existing_transaction:
                logger.info(f"Transaction with external id {transaction.external_id} already exists!")
            else:
                await send_stream.send_nowait(transaction)
                logger.info(f"Transaction with external id {transaction.external_id} doesn't exist")
