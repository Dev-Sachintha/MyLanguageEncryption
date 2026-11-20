# My Language Encryption - Extended Custom Mapping

## New features
- Add mapping rows with the **+ ADD** button.
- Map uppercase/lowercase English letters, digits and symbols.
- Remove selected mapping rows.
- Save custom mappings in `language_mapping.json`.
- Reset to the original A-Z Sinhala mapping.
- Longest-token matching supports multi-character source/replacement entries.

## Run on Windows
```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Add examples
Open **EDIT LANGUAGE** then click **+ ADD** and enter:
- `a` -> `අ`
- `7` -> `෭`
- `@` -> `ඞ`
- `#` -> `♜`

Click **Save** to apply and save the mapping.

## Important
This is a custom substitution system for learning/text conversion, not secure
cryptography. Do not store real passwords or sensitive information with it.
