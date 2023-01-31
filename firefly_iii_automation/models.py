import enum
from copy import deepcopy
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional

import maya
from firefly_iii_client.model.transaction_split_store import TransactionSplitStore
from firefly_iii_client.model.transaction_store import TransactionStore
from firefly_iii_client.model.transaction_type_property import TransactionTypeProperty


class FireflyTransactionTypes(enum.Enum):
    WITHDRAWAL = 'withdrawal'
    DEPOSIT = 'deposit'
    TRANSFER = 'transfer'


@dataclass()
class FireflyTransaction:
    external_id: str
    description: str
    date: datetime
    source_account: str
    destination_account: str
    amount: float
    type: FireflyTransactionTypes
    tags: list[str] = field(default_factory=lambda: ['python-script'])
    category_name: Optional[str] = None
    currency_code: Optional[str] = None
    foreign_amount: Optional[str] = None
    foreign_currency_code: Optional[str] = None
    notes: Optional[str] = None

    def to_transaction_store(self):
        spit_store_kwargs = dict(
            description=self.description,
            amount=str(self.amount),
            category_name=self.category_name,
            currency_code=self.currency_code,
            date=self.date,
            destination_name=self.destination_account,
            external_id=self.external_id,
            notes=self.notes,
            source_name=self.source_account,
            tags=self.tags,
            type=TransactionTypeProperty(self.type.value),
        )

        if self.foreign_amount:
            spit_store_kwargs['foreign_amount'] = self.foreign_amount
            spit_store_kwargs['foreign_currency_code'] = self.foreign_currency_code

        return TransactionStore(
            apply_rules=False,
            error_if_duplicate_hash=False,
            fire_webhooks=True,
            transactions=[
                TransactionSplitStore(**spit_store_kwargs),
            ],
        )

    def to_dict(self):
        clone = deepcopy(self)
        clone.type = clone.type.value
        return asdict(clone)

    @classmethod
    def from_dict(cls, dict):
        dict_clone = deepcopy(dict)
        dict_clone['type'] = FireflyTransactionTypes[dict_clone['type'].upper()]

        instance = cls(**dict_clone)
        if isinstance(instance.date, str):
            instance.date = maya.parse(instance.date).datetime()
        return instance
