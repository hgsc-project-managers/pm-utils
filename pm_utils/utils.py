"""
Add common utility modules that can be imported to other scripts
"""

# First come standard libraries, in alphabetical order
import csv
import re

# After a blank line, import third-party libraries

# After another blank line, import local libraries


def normalize_name(field_name):
    """lowercase with underscores, etc"""
    fixes = (
        (r"/", "_per_"),
        (r"%", "_pct_"),
        (r"\W", "_"),
        (r"^_+", ""),  # remove '_' if field_name begins with '_'
        (r"_+$", ""),
        (r"__+", "_"),
    )
    result = field_name.strip().lower() or None
    # result = field_name.strip().upper() or None
    if result:
        if result.endswith("?"):
            if not re.match(r"is[_\W]", result):
                result = "is_" + result
        for pattern, replacement in fixes:
            result = re.sub(pattern, replacement, result)
    return result


class TsvDialect(csv.Dialect):
    """Standard Unix-style TSV format."""
    delimiter = "\t"
    doublequote = False
    escapechar = "\\"
    lineterminator = "\n"
    extrasaction = "ignore"
    quotechar = '"'
    quoting = csv.QUOTE_MINIMAL
    skipinitialspace = False
