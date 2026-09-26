"""CSV/Python oracle independent of SQL templates. Live scores are separate."""
import argparse
from collections import defaultdict
import csv
from datetime import datetime, timezone
import json
import math
import statistics
from .agent import analyze, OpenAIPlanner
from .catalog import CATALOG
from .data import ROOT

def oracle():
    with (ROOT/'data'/'bank-additional-full.csv').open(encoding='utf-8') as stream:
        rows = list(csv.DictReader(stream, delimiter=';'))
    def stats(group):
        positives = sum(row['y']=='yes' for row in group)
        return [len(group), positives, round(100*positives/len(group),4)]
    answers = {'overall': [stats(rows)]}
    for name, field in [('channel','contact'),('job','job'),('education','education'),('month','month'),('history','poutcome'),('loan','loan')]:
        groups = defaultdict(list)
        for row in rows:
            groups[row[field]].append(row)
        answers[name] = [[value,*stats(group)] for value,group in groups.items()]
    for name in ['age','frequency']:
        groups = defaultdict(list)
        for row in rows:
            a, c = int(row['age']), int(row['campaign'])
            value = ('<30' if a<30 else '30-44' if a<45 else '45-59' if a<60 else '60+') if name=='age' else ('1' if c==1 else '2-3' if c<=3 else '4-5' if c<=5 else '6+')
            groups[value].append(row)
        answers[name] = [[value,*stats(group)] for value,group in groups.items()]
    groups = defaultdict(list)
    for row in rows:
        groups[(row['contact'],row['job'])].append(row)
    ranked = defaultdict(list)
    for (channel,job), group in groups.items():
        if len(group)>=100:
            n, _, rate = stats(group)
            ranked[channel].append([channel,job,n,rate])
    answers['rank'] = []
    for channel, segments in ranked.items():
        for rank, row in enumerate(sorted(segments, key=lambda row:(-row[3],row[1]))[:3],1):
            answers['rank'].append([*row,rank])
    answers['quality'] = [[sum(row[field]=='unknown' for row in rows) for field in ['job','education','loan']]]
    return answers

def same(actual, expected):
    # Compare unordered result sets; numeric tolerance accounts for SQL rounding.
    if len(actual)!=len(expected):
        return False
    actual = sorted(actual, key=lambda row: str(row[:1]))
    expected = sorted(expected, key=lambda row: str(row[:1]))
    # Rank output has two string dimensions, so stable compound sort is necessary.
    def key(row):
        return tuple(str(cell) for cell in row if isinstance(cell,str))
    actual, expected = sorted(actual,key=key), sorted(expected,key=key)
    return all(len(a)==len(b) and all(
        math.isclose(x,y,abs_tol=.0002) if isinstance(x,(int,float)) and isinstance(y,(int,float)) else x==y
        for x,y in zip(a,b)) for a,b in zip(actual,expected))

def evaluate(live=False):
    reference = oracle()
    checks = []
    for name,item in CATALOG.items():
        question = item['question']
        if live and name in reference:
            # Output contract makes automated comparison auditable, not a semantic judge.
            from .sql import execute
            cols = execute(item['sql'])['columns']
            question += ' 输出字段顺序为：'+', '.join(cols)+'。数值百分比保留4位小数。'
        result = analyze(question, planner=OpenAIPlanner() if live else None,
                         demo_id=None if live else name)
        expected_status = 'refuse' if 'reason' in item else 'ok'
        passed = result['status']==expected_status
        if expected_status=='ok':
            passed = passed and same(result.get('table',{}).get('rows',[]), reference[name])
        checks.append({'id': name, 'question': question, 'passed': passed,
                       'expected_status': expected_status, 'result': result})
    report = {'mode':'live' if live else 'demo', 'timestamp':datetime.now(timezone.utc).isoformat(),
              'scope':'15 fixed catalog questions; CSV oracle; not a general NL-to-SQL accuracy claim',
              'passed':sum(case['passed'] for case in checks), 'total':len(checks),
              'median_ms':statistics.median(case['result']['elapsed_ms'] for case in checks),
              'cases':checks}
    path = ROOT/'reports'/('live-evaluation.json' if live else 'demo-evaluation.json')
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({key:value for key,value in report.items() if key!='cases'},ensure_ascii=True,indent=2))
    return report

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--live',action='store_true',help='Calls configured OpenAI model; incurs API usage')
    args = parser.parse_args()
    report = evaluate(args.live)
    raise SystemExit(0 if report['passed']==report['total'] else 1)
