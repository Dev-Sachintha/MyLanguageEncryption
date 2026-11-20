import json
from pathlib import Path

DEFAULT_MAPPING = {
    "A": "ව", "B": "ක", "C": "ග", "D": "ස", "E": "න",
    "F": "ම", "G": "ර", "H": "ත", "I": "ද", "J": "ප",
    "K": "ල", "L": "ය", "M": "බ", "N": "හ", "O": "ජ",
    "P": "ට", "Q": "ඩ", "R": "ච", "S": "ඡ", "T": "ඤ",
    "U": "ණ", "V": "ථ", "W": "ධ", "X": "භ", "Y": "ශ",
    "Z": "ෂ",
}

MAPPING_FILE = Path(__file__).resolve().parent.parent / "language_mapping.json"


def load_mapping():
    if not MAPPING_FILE.exists():
        return DEFAULT_MAPPING.copy()
    try:
        data = json.loads(MAPPING_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return DEFAULT_MAPPING.copy()
        mapping = {str(k): str(v) for k, v in data.items()}
        return mapping if not validate_mapping(mapping) else DEFAULT_MAPPING.copy()
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return DEFAULT_MAPPING.copy()


def save_mapping(mapping):
    MAPPING_FILE.write_text(
        json.dumps(mapping, ensure_ascii=False, indent=4),
        encoding="utf-8"
    )


def validate_mapping(mapping):
    if not mapping:
        return "Add at least one character mapping."

    keys = list(mapping.keys())
    values = [str(value).strip() for value in mapping.values()]

    if any(not str(key).strip() for key in keys):
        return "Original characters cannot be empty."
    if any(not value for value in values):
        return "Your replacement characters cannot be empty."
    if len(set(keys)) != len(keys):
        return "Each original character must be unique."
    if len(set(values)) != len(values):
        return "Each replacement must be unique so decryption works."

    return ""


def _build_lookup(mapping):
    lookup = dict(mapping)
    for key, value in mapping.items():
        if len(key) == 1 and key.isalpha():
            lower_key = key.lower()
            upper_key = key.upper()
            if lower_key not in lookup:
                lookup[lower_key] = value
            if upper_key not in lookup:
                lookup[upper_key] = value
    return lookup


def _replace_longest_first(text, mapping):
    tokens = sorted(mapping.keys(), key=len, reverse=True)
    result = []
    i = 0
    while i < len(text):
        match = next((token for token in tokens if text.startswith(token, i)), None)
        if match is None:
            result.append(text[i])
            i += 1
        else:
            result.append(mapping[match])
            i += len(match)
    return "".join(result)


def encrypt_text(text, mapping):
    return _replace_longest_first(text, _build_lookup(mapping))


def decrypt_text(text, mapping):
    reverse = {value: key for key, value in mapping.items()}
    return _replace_longest_first(text, reverse)
