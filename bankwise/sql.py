"""Defense in depth: AST checks, read-only connection, authorizer, VM budget."""
from pathlib import Path
from contextlib import closing
import sqlite3
import time
import sqlglot
from sqlglot import exp
from .data import DB

class QueryError(ValueError):
    pass

FUNCTIONS = {'count', 'sum', 'avg', 'min', 'max', 'round', 'abs', 'coalesce',
             'nullif', 'cast', 'lower', 'upper', 'length', 'substr', 'substring',
             'row_number', 'rank', 'dense_rank', 'lag', 'lead', 'total', 'typeof'}

def validate(sql):
    if not isinstance(sql, str) or len(sql) > 12000:
        raise QueryError('SQL must be text under 12,000 characters')
    try:
        statements = sqlglot.parse(sql, read='sqlite')
    except sqlglot.errors.ParseError as exc:
        raise QueryError('Invalid SQLite syntax') from exc
    if len(statements) != 1 or not isinstance(statements[0], exp.Select):
        raise QueryError('Only one SELECT statement is allowed')
    tree = statements[0]
    forbidden = {'Insert', 'Update', 'Delete', 'Drop', 'Create', 'Alter', 'Command',
                 'Attach', 'Detach', 'Pragma', 'Into', 'Transaction', 'Merge'}
    if any(type(node).__name__ in forbidden for node in tree.walk()):
        raise QueryError('Write operations are forbidden')
    if any(node.args.get('recursive') for node in tree.find_all(exp.With)):
        raise QueryError('Recursive CTEs are disabled')
    ctes = {node.alias.lower() for node in tree.find_all(exp.CTE)}
    for table in tree.find_all(exp.Table):
        if table.catalog or table.db or table.name.lower() not in {'bank_contacts'} | ctes:
            raise QueryError('Only bank_contacts and local CTEs can be queried')
    return sql

def execute(sql, db=DB, max_rows=200, seconds=3, vm_steps=2_000_000):
    validate(sql)
    start = time.monotonic()
    conn = sqlite3.connect(Path(db).resolve().as_uri() + '?mode=ro', uri=True)
    conn.execute('PRAGMA query_only=ON')
    calls = 0
    def budget():
        nonlocal calls
        calls += 1
        return int(calls * 1000 > vm_steps or time.monotonic() - start > seconds)
    def authorize(action, arg1, arg2, database, trigger):
        if action == sqlite3.SQLITE_READ:
            return sqlite3.SQLITE_OK if arg1 == 'bank_contacts' else sqlite3.SQLITE_DENY
        if action == sqlite3.SQLITE_FUNCTION:
            return sqlite3.SQLITE_OK if (arg2 or '').lower() in FUNCTIONS else sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK if action == sqlite3.SQLITE_SELECT else sqlite3.SQLITE_DENY
    conn.set_authorizer(authorize)
    conn.set_progress_handler(budget, 1000)
    try:
        cur = conn.execute(sql)
        columns = [x[0] for x in cur.description]
        rows = cur.fetchmany(max_rows + 1)
        return {'columns': columns, 'rows': [list(r) for r in rows[:max_rows]],
                'truncated': len(rows) > max_rows, 'elapsed_ms': round((time.monotonic()-start)*1000, 2)}
    except sqlite3.Error as exc:
        raise QueryError(str(exc)) from exc
    finally:
        conn.close()

def schema(db=DB):
    with closing(sqlite3.connect(Path(db).resolve().as_uri() + '?mode=ro', uri=True)) as conn:
        return [{'name': row[1], 'type': row[2]} for row in conn.execute('PRAGMA table_info(bank_contacts)')]
