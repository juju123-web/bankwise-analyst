"""Session-owned CSV datasets; original column names are retained."""
import csv
import io
import sqlite3
import tempfile
from pathlib import Path

import pandas as pd

MAX_BYTES = 10_000_000
MAX_ROWS = 100_000
MAX_COLUMNS = 100


def read_csv(payload):
    if not payload or len(payload) > MAX_BYTES:
        raise ValueError('CSV 不能为空，且不得超过 10 MB。 / CSV must be nonempty and at most 10 MB.')
    try:
        text = payload.decode('utf-8-sig')
        try:
            delimiter = csv.Sniffer().sniff(text[:8192], delimiters=',;\t|').delimiter
        except csv.Error:
            delimiter = ','
        records = csv.reader(io.StringIO(text), delimiter=delimiter, strict=True)
        names = next(records)
        if not names or len(names) > MAX_COLUMNS or any(not n.strip() or '\x00' in n or len(n) > 128 for n in names):
            raise ValueError('请提供 1–100 个非空字段名，每个字段名不超过 128 字。')
        if len({n.casefold() for n in names}) != len(names):
            raise ValueError('字段名不能重复（不区分大小写）。')
        rows = []
        for row in records:
            if not row:
                continue
            if len(row) != len(names):
                raise ValueError('某些行的字段数量与表头不一致。')
            rows.append(row)
            if len(rows) > MAX_ROWS:
                raise ValueError('最多支持 100,000 行。')
        if not rows:
            raise ValueError('CSV 必须包含表头和至少一行数据。')
    except (UnicodeError, csv.Error, StopIteration) as exc:
        raise ValueError('无法读取 CSV，请使用 UTF-8 编码并检查分隔符与引号。') from exc
    frame = pd.DataFrame(rows, columns=names)
    for name in names:
        series = frame[name].replace('', None)
        # Preserve identifiers with leading zeros and leave dates as supplied text.
        numeric = pd.to_numeric(series, errors='coerce')
        leading_zero = series.dropna().str.match(r'^[+-]?0\d').any()
        if not leading_zero and numeric.notna().sum() == series.notna().sum():
            frame[name] = numeric
        else:
            frame[name] = series
    return frame


def create_dataset(payload):
    frame = read_csv(payload)
    folder = tempfile.TemporaryDirectory(prefix='bankwise-')
    db = Path(folder.name) / 'dataset.db'
    try:
        with sqlite3.connect(db) as conn:
            frame.to_sql('bank_contacts', conn, index=False)
    except Exception:
        folder.cleanup()
        raise
    return {'owner': folder, 'db': db, 'rows': len(frame), 'columns': len(frame.columns),
            'preview': frame.head(20)}
