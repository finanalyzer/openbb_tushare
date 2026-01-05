import re
from mysharelib.tools import normalize_symbol

_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_TUSHARE_SUPPORTED_MARKETS = {"SH", "SZ", "BJ", "HK"}


def normalize_tushare_symbol_list(symbols: str) -> str:
    """Normalize a comma-separated list of user symbols into Tushare ts_code format.

    Accepts Yahoo-style suffixes (e.g., .SS) and converts them to Tushare expected suffixes.
    Raises a ValueError with a clear message for unsupported markets.
    """

    if not isinstance(symbols, str) or not symbols.strip():
        raise ValueError("Invalid 'symbol' format. Expected a non-empty string.")

    normalized: list[str] = []
    for raw in [s.strip() for s in symbols.split(",") if s.strip()]:
        _, full, market = normalize_symbol(raw)
        if market not in _TUSHARE_SUPPORTED_MARKETS:
            raise ValueError(
                f"Invalid 'symbol' market for Tushare: '{raw}'. Expected CN (.SS/.SZ/.BJ) or HK (.HK)."
            )
        normalized.append(full)

    return ",".join(normalized)


def validate_iso_yyyy_mm_dd(value: object, field_name: str) -> object:
    """Enforce YYYY-MM-DD when date fields are provided as strings."""

    if value is None:
        return value
    if isinstance(value, str) and not _ISO_DATE_RE.match(value):
        raise ValueError(f"Invalid '{field_name}' format. Expected YYYY-MM-DD.")
    return value