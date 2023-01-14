import json
from datetime import date, datetime


def serializer(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    raise TypeError(f"Type {type(obj)} not serializable")


def dumps(obj):
    return json.dumps(obj, default=serializer)
