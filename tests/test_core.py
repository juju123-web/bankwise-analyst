import sqlite3
import pytest
from bankwise.sql import execute, QueryError
from bankwise.agent import analyze

@pytest.fixture
def db(tmp_path):
    path = tmp_path / 'fixture.db'
    with sqlite3.connect(path) as conn:
        conn.execute('CREATE TABLE bank_contacts(observation_id INTEGER, contact TEXT, subscribed INTEGER)')
        conn.executemany('INSERT INTO bank_contacts VALUES (?,?,?)', [(1,'cellular',1),(2,'cellular',0),(3,'telephone',0)])
    return path

def test_fraction_and_denominator(db):
    result = execute('SELECT contact, COUNT(*), 100.0*AVG(subscribed) FROM bank_contacts GROUP BY contact ORDER BY contact', db)
    assert result['rows'] == [['cellular',2,50.0],['telephone',1,0.0]]

@pytest.mark.parametrize('sql', [
    'DELETE FROM bank_contacts', 'DROP TABLE bank_contacts',
    'SELECT 1; DELETE FROM bank_contacts', "ATTACH DATABASE 'x' AS other",
    'PRAGMA table_info(bank_contacts)', 'SELECT * FROM sqlite_master',
    "SELECT load_extension('x')", 'SELECT randomblob(100000000)',
    'SELECT * FROM main.bank_contacts',
    'WITH RECURSIVE x(n) AS (SELECT 1 UNION ALL SELECT n+1 FROM x) SELECT * FROM x',
    'CREATE TABLE copy AS SELECT * FROM bank_contacts',
])
def test_attacks_rejected(db, sql):
    with pytest.raises(QueryError):
        execute(sql, db)
    assert execute('SELECT COUNT(*) FROM bank_contacts', db)['rows']==[[3]]

def test_limit_and_empty(db):
    assert execute('SELECT * FROM bank_contacts', db, max_rows=2)['truncated'] is True
    assert execute('SELECT * FROM bank_contacts WHERE 0', db)['rows'] == []

def test_budget(db):
    with pytest.raises(QueryError, match='interrupted'):
        execute('SELECT COUNT(*) FROM bank_contacts a CROSS JOIN bank_contacts b CROSS JOIN bank_contacts c CROSS JOIN bank_contacts d CROSS JOIN bank_contacts e CROSS JOIN bank_contacts f CROSS JOIN bank_contacts g', db, vm_steps=1000)

def test_cte_window(db):
    result = execute('WITH x AS (SELECT contact, subscribed FROM bank_contacts) SELECT contact, ROW_NUMBER() OVER (ORDER BY subscribed DESC) AS r FROM x', db)
    assert len(result['rows'])==3

def test_repair(db):
    calls = []
    def planner(question, columns, error):
        calls.append(error)
        return {'status':'query', 'sql':'SELECT nonexistent FROM bank_contacts' if not error else 'SELECT COUNT(*) AS n FROM bank_contacts'}
    result = analyze('数量', planner=planner, db=db)
    assert result['status']=='ok' and result['table']['rows']==[[3]]
    assert len(calls)==2 and 'nonexistent' in calls[1]['message']

def test_bounded_failure(db):
    result = analyze('数量', planner=lambda *args: {'status':'query','sql':'DELETE FROM bank_contacts'}, db=db)
    assert result['status']=='error'
    assert len([t for t in result['trace'] if t['step']=='repair_needed'])==2

def test_refusal(db):
    result = analyze('收入', planner=lambda *args: {'status':'refuse','explanation':'没有收入字段'}, db=db)
    assert result['status']=='refuse'
    assert not any(t['step']=='execute' for t in result['trace'])

def test_demo_not_free_language(db):
    assert analyze('随便说一句', db=db)['status']=='clarify'

def test_provider_error_no_secret(db):
    def fail(*args):
        raise RuntimeError('secret-key-123')
    result = analyze('分析', planner=fail, db=db)
    assert result['status']=='error' and 'secret-key-123' not in str(result)

def test_invalid_json_repair(db):
    calls = []
    def planner(*args):
        calls.append(1)
        return [] if len(calls)==1 else {'status':'query', 'sql':'SELECT COUNT(*) FROM bank_contacts'}
    assert analyze('数量', planner=planner, db=db)['status']=='ok'

def test_empty_question(db):
    assert analyze('', db=db)['status']=='clarify'
