from datetime import datetime, timezone


def utcnow():
    """UTC atual sem tzinfo, compatível com as colunas DateTime do SQLite.

    Substitui o deprecated datetime.utcnow().
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


def percentage(part, total):
    if total == 0:
        return 0
    return round((part / total) * 100, 2)
