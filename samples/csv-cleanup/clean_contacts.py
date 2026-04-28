import csv
import hashlib
import re
from pathlib import Path

base = Path(__file__).resolve().parent
source = base / 'messy_contacts.csv'
cleaned = base / 'cleaned_contacts.csv'
report = base / 'cleanup_report.md'

def norm_email(v: str) -> str:
    return (v or '').strip().lower()

def norm_phone(v: str) -> str:
    digits = re.sub(r'\D+', '', v or '')
    if len(digits) == 10:
        return f'({digits[:3]}) {digits[3:6]}-{digits[6:]}'
    return digits

def title(v: str) -> str:
    return ' '.join((v or '').strip().split()).title()

rows = []
with source.open(newline='', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for raw in reader:
        item = {k.strip().lower(): (v or '').strip() for k, v in raw.items()}
        name = title(item.get('name', ''))
        email = norm_email(item.get('email', ''))
        phone = norm_phone(item.get('phone', ''))
        city = title(item.get('city', ''))
        service = title(item.get('service', ''))
        notes = ' '.join(item.get('notes', '').split())
        if not any([name, email, phone, city, service]):
            continue
        rows.append({'name': name, 'email': email, 'phone': phone, 'city': city, 'service': service, 'notes': notes})

seen = set()
unique = []
duplicates = []
missing = []
for r in rows:
    key = (r['email'] or r['name'].lower(), r['phone'])
    if key in seen:
        duplicates.append(r)
        continue
    seen.add(key)
    if not r['email']:
        missing.append({'name': r['name'], 'missing': 'email'})
    unique.append(r)

with cleaned.open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['name', 'email', 'phone', 'city', 'service', 'notes'])
    writer.writeheader()
    writer.writerows(unique)

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

report.write_text(f'''# CSV Cleanup Portfolio Proof

Input rows read: {len(rows)}
Cleaned unique rows: {len(unique)}
Duplicate rows removed: {len(duplicates)}
Rows needing follow-up: {len(missing)}

## What was fixed
- Header whitespace normalized.
- Email lowercased.
- Phone numbers normalized.
- City/service title-cased.
- Blank/bad row removed.
- Duplicate contact removed.
- Missing-email row flagged.

## Proof
- Input SHA256: {sha(source)}
- Output SHA256: {sha(cleaned)}

## Buyer-facing deliverable
A cleaned CSV plus a short report explaining what changed and what still needs human/business follow-up.
''', encoding='utf-8')
print({'ok': True, 'input': str(source), 'output': str(cleaned), 'report': str(report), 'unique': len(unique), 'duplicates': len(duplicates), 'missing': len(missing)})
