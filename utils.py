from typing import Any, Iterable

def isnan(x: Any) -> bool:
    return x != x


def format_series(v: Iterable[str], backticks: bool = True, conjunction: str = 'and'):
    q = '`' if backticks else ''
    items = [f'{q}{item}{q}' for item in v]
    if (n := len(items)) == 1:
        return items[0]
    if n == 2:
        return f'{items[0]} {conjunction} {items[1]}'
    *rest, last = items
    rest_s = ', '.join(rest)
    last_s = f', {conjunction} {last}'
    return rest_s + last_s
