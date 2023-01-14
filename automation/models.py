import enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass()
class ParsedReport:
    id: str
    description: str
    date: datetime
    source: str
    destination: str
    currency_code: str
    foreign_currency_code: Optional[str] = None
    debit: float = 0
    credit: float = 0


class FireflyTransactionTypes(enum.Enum):
    WITHDRAWAL = 'withdrawal'
    DEPOSIT = 'deposit'
    TRANSFER = 'transfer'


@dataclass()
class FireflyTransaction:
    external_id: str
    date: str
    source_account: str
    destination_account: str
    amount: str
    type: FireflyTransactionTypes
    tags: list[str]
    category_name: Optional[str] = None
    currency_code: Optional[str] = None
    foreign_amount: Optional[str] = None
    foreign_currency_code: Optional[str] = None
    notes: Optional[str] = None

    @classmethod
    def from_parsed_report(cls, report, transaction_type):
        """
        :param ParsedReport report:
        :param FireflyTransactionTypes transaction_type:
        :return:
        """
        return cls(
            external_id=report.id,
            notes=report.description,
            date=report.date.isoformat(),
            source_account=report.source,
            destination_account=report.destination,
            amount=str(abs(report.credit or report.debit)),
            type=transaction_type,
            tags=['python-script'],
            currency_code=report.currency_code,
            foreign_currency_code=report.foreign_currency_code,
        )
