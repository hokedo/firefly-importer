import asyncio
import dataclasses
import logging
from typing import AsyncIterator

import firefly_iii_client
from aiocache import cached
from aiofiles.tempfile import _temporary_directory
from aiopath import AsyncPath
from anyio import create_memory_object_stream
from anyio.streams.memory import MemoryObjectSendStream
# noinspection PyUnresolvedReferences
from h2o_wave import Q, main, app, ui

from firefly_iii_automation.firefly._async import get_all_accounts, get_all_categories, \
    get_all_descriptions as _get_all_descriptions, get_all_asset_accounts, find_transaction_by_external_id, \
    create_new_transaction
from firefly_iii_automation.models import FireflyTransactionTypes, FireflyTransaction
from firefly_iii_automation.transactions_parsers import parse_bt_transaction_report

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

CURRENCIES = ['RON', 'EUR']


@app('/')
async def serve(q: Q):
    form_items = []

    if q.args.file_upload or q.client.transactions:
        get_next_transaction = False

        if q.client.current_file is None:
            # File was uploaded just now
            q.client.temp_dir = await _temporary_directory()
            q.client.current_file = await q.site.download(q.args.file_upload[0], q.client.temp_dir.name)
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
            get_next_transaction = True
        elif not q.args.skip_button:
            # Insert currently displayed transaction
            transaction_dict = {}
            for field in dataclasses.fields(FireflyTransaction):
                transaction_dict[field.name] = q.args[field.name]

            transaction_dict['external_id'] = q.client.current_transaction.external_id
            transaction = FireflyTransaction.from_dict(transaction_dict)

            try:
                await create_new_transaction(transaction)
                logger.info(f"Transaction with external id {transaction.external_id} successfully inserted")
                get_next_transaction = True

                # add account to autocomplete list if it's a new entry
                if transaction.source_account not in q.client.accounts:
                    q.client.accounts = sorted(q.client.accounts + [transaction.source_account])

                if transaction.destination_account not in q.client.accounts:
                    q.client.accounts = sorted(q.client.accounts + [transaction.destination_account])

                # add categories to autocomplete list if it's a new entry
                if transaction.category_name and transaction.category_name not in q.client.categories:
                    q.client.categories = sorted(q.client.categories + [transaction.category_name])

                # add descriptions to autocomplete list if it's a new entry
                if transaction.description not in q.client.descriptions:
                    q.client.descriptions = sorted(q.client.descriptions + [transaction.description])

                form_items.append(ui.message_bar(type='success', text='Successfully inserted transaction!'))

            except (Exception, firefly_iii_client.exceptions.ApiException) as ex:
                logger.exception(ex)
                logger.error('Failed to insert transaction!')
                form_items.append(ui.message_bar(type='blocked', text='Failed to insert transaction!'))

        if q.args.skip_button:
            form_items.append(ui.message_bar(
                type='info',
                text=f'Skipped transaction with id {q.client.current_transaction.external_id}'
            ))
            get_next_transaction = True

        if get_next_transaction:
            try:
                # Get the next transaction to show
                q.client.current_transaction = await anext(q.client.transactions)

            except StopAsyncIteration as ex:
                # Processed all transactions.
                # Reset the UI
                logger.info("Finished transactions")
                q.client.transactions = None
                q.client.current_transaction = None
                q.client.current_file = None
                await q.client.temp_dir.close()
                form_items.append(ui.message_bar(type='info', text='Finished processing transactions'))

        if q.client.current_transaction:
            # Hide the file upload input and show the transaction fields
            form_items += await build_form_transaction_fields(q.client.current_transaction, q)

    if not q.client.transactions:
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


async def build_form_transaction_fields(transaction: FireflyTransaction, q):
    errors = await get_form_errors(transaction)
    return [
        ui.inline(items=[
            ui.combobox(name='type', label='Type', choices=['Withdrawal', 'Deposit', 'Transfer'], width='25%',
                        required=True, value=transaction.type.value.capitalize()),
            ui.combobox(name='description', label='Description', value=transaction.description,
                        choices=q.client.descriptions, width='75%',
                        required=True, error=errors.get('description')),
        ]),
        ui.inline(items=[
            ui.combobox(name='source_account', label='Source Account',
                        choices=q.client.accounts, value=transaction.source_account,
                        width='50%', required=True, error=errors.get('source_account')),
            ui.combobox(name='destination_account', label='Destination Account',
                        choices=q.client.accounts, value=transaction.destination_account,
                        width='50%', required=True, error=errors.get('destination_account')),
        ]),
        ui.inline(items=[
            ui.date_picker(name='date', label='Date', value=transaction.date.isoformat(), width="50%"),
            ui.combobox(name='category_name', label='Category Name',
                        choices=q.client.categories, value=transaction.category_name,
                        width="50%")
        ]),
        ui.inline(items=[
            ui.textbox(name='amount', label='Amount', width="50%", value=str(transaction.amount),
                       required=True, error=errors.get('amount')),
            ui.combobox(name='currency_code', label='Currency',
                        choices=CURRENCIES, width="50%", value=transaction.currency_code)
        ]),
        ui.inline(items=[
            ui.textbox(name='foreign_amount', label='Foreign Amount',
                       value=str(transaction.foreign_amount or ''), width="50%", error=errors.get('foreign_amount')),
            ui.combobox(name='foreign_currency_code', label='Foreign Currency',
                        choices=CURRENCIES, value=transaction.foreign_currency_code, width="50%")
        ]),
        ui.textbox(name='notes', label='notes', width="100%", multiline=True, value=transaction.notes),
        ui.buttons(
            justify='center',
            items=[ui.button(name='skip_button', label='Skip', width='100%', primary=False)]
        ),
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
        await send_stream.aclose()


async def get_form_errors(transaction: FireflyTransaction):
    errors = {}
    if transaction.source_account and 'unknown' in transaction.source_account.lower():
        errors['source_account'] = 'Unknown account!'

    if transaction.destination_account and 'unknown' in transaction.destination_account.lower():
        errors['destination_account'] = 'Unknown account!'

    if not transaction.description:
        errors['destination'] = 'Empty value not allowed!'

    if transaction.amount:
        try:
            float(transaction.amount)
        except:
            errors['amount'] = 'Bad value!'

    if transaction.foreign_amount:
        try:
            float(transaction.foreign_amount)
        except:
            errors['foreign_amount'] = 'Bad value!'

    return errors
