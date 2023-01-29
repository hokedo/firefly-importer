import csv
import re
import typing
from datetime import datetime

import aiocsv
from aiopath import AsyncPath
from anyio import AsyncFile

from ..exceptions import NoIBANException
from ..models import FireflyTransaction, FireflyTransactionTypes

CATEGORIES_STRINGS_MAPS = {
    "Food": ["PayUtazz.ro", "GLOVO", "Glovo", "KFC KIOSC"],
    "Transport": ["BOLT.EU", "UBER TRIP", "OMV", "EPinterregional.ro"],
    "Groceries": ["MEGAIMAGE", "GUSTINO", "LIDL", "SELGROS", "KAUFLAND"],
    "Going out": ["COPACUL DE CAFEA", "BUSINESS BISTRO CAFE"],
    "Cheltuieli": ["NETFLIX.COM", "SPLITWISE", "RCS AND RDS", "Amazon Video", "WWW.ORANGE.RO"]
}


async def parse_bt_transaction_report(file_obj: AsyncFile):
    """
    :param typing.TextIO file_obj: Opened File object
    :return:
    """
    currency_code = 'RON'
    # Skip first 16 lines
    iban = None
    for _ in range(16):
        line = await file_obj.readline()

        if 'numar cont' in line.lower():
            iban, currency_code = line.split(",")[1].split(" ")

    if not iban:
        raise NoIBANException()

    csv_reader = aiocsv.AsyncDictReader(file_obj)

    async for row in csv_reader:
        transaction_reference = row['Referinta tranzactiei']
        original_description = row['Descriere']
        debit = abs(float(row['Debit'])) if row['Debit'] else 0
        credit = abs(float(row['Credit'])) if row['Credit'] else 0

        date_match = re.search(r';POS (\d{2}/\d{2}/\d{4}) ', original_description)
        if date_match:
            # date when transaction got initiated
            date = datetime.strptime(date_match.group(1), '%d/%m/%Y')

        else:
            # this is actually the date when it got processed
            date = datetime.strptime(row['Data tranzactie'], '%Y-%m-%d')

        description, category, destination = get_description_category_destination(
            original_description,
            debit,
            credit
        )

        transaction_type = get_transaction_type(original_description, debit, credit)

        source_account = iban
        destination_account = destination
        if transaction_type is FireflyTransactionTypes.DEPOSIT:
            source_account = destination
            destination_account = iban

        yield FireflyTransaction(
            external_id=transaction_reference,
            description=description,
            date=date,
            source_account=source_account,
            destination_account=destination_account,
            amount=debit or credit,
            currency_code=currency_code,
            category_name=category,
            type=transaction_type,
            notes=original_description
        )


def get_transaction_type(bt_description, debit, credit):
    if credit and not debit:
        return FireflyTransactionTypes.DEPOSIT

    if 'Transfer intern - canal electronic' in bt_description:
        return FireflyTransactionTypes.TRANSFER

    return FireflyTransactionTypes.WITHDRAWAL


def get_description_category_destination(bt_description, debit, credit):
    category = None
    found_string = None
    description = ''
    destination = "Unknown"

    destination_match = re.search(r'TID:?[\d\w]+ (.+)\s{2}', bt_description)
    if destination_match:
        destination = destination_match.group(1)

    for key, strings in CATEGORIES_STRINGS_MAPS.items():
        for string in strings:
            if string in bt_description:
                category = key
                found_string = string
                destination = found_string.lower().capitalize()
                break

    if category == 'Food':
        if debit > 150 and 'tazz' in found_string.lower() or 'glovo' in found_string.lower():
            category = 'Groceries'
        else:
            description = 'Mancare comandata'

        if 'tazz' in found_string.lower():
            destination = 'Tazz'

    if category == 'Groceries':
        description = f'{destination} cumparaturi'

    if category == "Transport":
        description = destination

        if "bolt" in found_string.lower():
            destination = 'Bolt'

            if debit < 13:
                description = 'Bolt scooter'

        if "uber" in found_string.lower():
            destination = 'Uber'

    if category == "Going out":
        description = "Iesire"

    if not category:
        if 'Transfer din card' in bt_description:
            sender = re.search(r'Transfer din card \d+ (.+) catre', bt_description).group(1)

            sender = sender.lower().title()
            description = f'Transfer {sender}'
            destination = sender

    if not description and destination != 'Unknown':
        description = f'Plata {destination}'

    return description, category, destination
