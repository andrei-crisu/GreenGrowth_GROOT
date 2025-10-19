"""Attempt to repair common issues in Firebase service account JSON private_key.

This script will:
- Load config/firebase-key.json
- If private_key contains literal "\\n" sequences (double-escaped), convert them into real newlines in the in-memory string
- Rewrite the JSON with the fixed private_key (so json.dump will escape newlines correctly)
- Make a backup copy config/firebase-key.json.bak before changing

Run:
    python fix_firebase_key.py
"""
import io
import json
import os

p = os.path.join('config', 'firebase-key.json')
backup = p + '.bak'

if not os.path.exists(p):
    print('File not found:', p)
    raise SystemExit(1)

with io.open(p, 'r', encoding='utf-8') as f:
    raw = f.read()

# Quick sanity check: try to parse JSON
try:
    j = json.loads(raw)
except Exception as e:
    print('Failed to parse JSON:', e)
    raise

pk = j.get('private_key', '')
changed = False
print('Original private_key length:', len(pk))

# If the string contains literal backslash-n sequences (i.e. two characters \ and n), replace them with actual newline
if '\\\\n' in pk:
    print('Found "\\\\n" (quad-escaped) in private_key, reducing to "\\n"')
    pk = pk.replace('\\\\n', '\\n')
    changed = True

if '\\n' in pk:
    print('Found literal "\\n" sequences in private_key; converting to real newlines in memory')
    pk = pk.replace('\\n', '\n')
    changed = True

# Trim accidental surrounding quotes
if pk.startswith('"') and pk.endswith('"'):
    pk = pk[1:-1]
    changed = True

print('Fixed private_key length:', len(pk))

if changed:
    # Backup original file
    with io.open(backup, 'w', encoding='utf-8') as f:
        f.write(raw)
    print('Backup written to', backup)
    j['private_key'] = pk
    # Write back; json.dump will escape newlines correctly
    with io.open(p, 'w', encoding='utf-8') as f:
        json.dump(j, f, ensure_ascii=False, indent=2)
    print('Wrote fixed JSON to', p)
else:
    print('No changes required.')

print('Done. Now run: python test_firebase_init.py')