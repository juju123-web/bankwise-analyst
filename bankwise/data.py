"""Reproducible UCI ingestion; generated row IDs are NOT customer IDs."""
import csv
from contextlib import closing
import hashlib
import io
import json
from pathlib import Path
import sqlite3
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'data' / 'bank.db'
URL = 'https://archive.ics.uci.edu/static/public/222/bank+marketing.zip'
SOURCE = 'https://archive.ics.uci.edu/dataset/222/bank+marketing'
INTS = {'age', 'duration', 'campaign', 'pdays', 'previous'}
FLOATS = {'emp_var_rate', 'cons_price_idx', 'cons_conf_idx', 'euribor3m', 'nr_employed'}

def prepare():
    folder = DB.parent
    folder.mkdir(parents=True, exist_ok=True)
    archive = folder / 'bank-marketing.zip'
    if not archive.exists():
        with urllib.request.urlopen(URL, timeout=60) as response:
            payload = response.read(20_000_001)
        if len(payload) > 20_000_000:
            raise ValueError('Unexpected archive size')
        archive.write_bytes(payload)
    with zipfile.ZipFile(archive) as outer:
        with zipfile.ZipFile(io.BytesIO(outer.read('bank-additional.zip'))) as inner:
            raw = inner.read('bank-additional/bank-additional-full.csv')
    (folder / 'bank-additional-full.csv').write_bytes(raw)
    reader = csv.DictReader(io.StringIO(raw.decode('utf-8')), delimiter=';')
    original = reader.fieldnames
    fields = [name.replace('.', '_') for name in original]
    records = []
    for index, row in enumerate(reader, 1):
        values = []
        for old, name in zip(original, fields):
            value = row[old]
            values.append(int(value) if name in INTS else float(value) if name in FLOATS else value)
        records.append((index, *values, int(row['y'] == 'yes')))
    if len(records) != 41188 or sum(row[-1] for row in records) != 4640:
        raise ValueError('Source differs from the validated UCI release; review before ingesting')
    columns = ['observation_id INTEGER PRIMARY KEY'] + [
        f'"{name}" {"INTEGER" if name in INTS else "REAL" if name in FLOATS else "TEXT"} NOT NULL'
        for name in fields] + ['subscribed INTEGER NOT NULL CHECK(subscribed IN (0,1))']
    staging = folder / 'bank.staging.db'
    with closing(sqlite3.connect(staging)) as conn, conn:
        conn.execute('DROP TABLE IF EXISTS bank_contacts')
        conn.execute('CREATE TABLE bank_contacts (' + ','.join(columns) + ')')
        conn.executemany('INSERT INTO bank_contacts VALUES (' + ','.join('?' for _ in records[0]) + ')', records)
        conn.execute('CREATE INDEX idx_channel ON bank_contacts(contact)')
        conn.execute('CREATE INDEX idx_job ON bank_contacts(job)')
    staging.replace(DB)
    manifest = {'source': SOURCE, 'download': URL, 'license': 'CC BY 4.0',
                'authors': 'S. Moro, P. Rita, P. Cortez', 'rows': len(records), 'subscribed': 4640,
                'csv_sha256': hashlib.sha256(raw).hexdigest(),
                'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
                'grain': 'One source observation; no stable customer identifier or exact date.'}
    (folder / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    return manifest

if __name__ == '__main__':
    print(json.dumps(prepare(), indent=2))
