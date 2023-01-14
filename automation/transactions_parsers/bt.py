import csv
import json
from pathlib import Path


def parse_bt_transaction_report(path):
    """
    :param Path path: Path to CSV report
    :return:
    """

    with path.open() as f:
        # Skip first 16 lines
        for _ in range(16):
            next(f)
        csv_reader = csv.DictReader(f)

        for row in csv_reader:
            print(json.dumps(row))
