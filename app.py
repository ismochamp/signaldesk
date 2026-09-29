from local_host import Handler,serve,field,ROOT
from engine import predict
import csv,io,json,os,sqlite3
from datetime import datetime,timezone
from collections import Counter
DB=os.environ.get('APP_DB',str(ROOT/'data/triage.sqlite'))
def connect():
    from pathlib import Path
    Path(DB).parent.mkdir(parents=True,exist_ok=True)
    conn=sqlite3.connect(DB,timeout=15);conn.row_factory=sqlite3.Row
    conn.executescript('CREATE TABLE IF NOT EXISTS examples(id INTEGER PRIMARY KEY,text TEXT NOT NULL,label TEXT NOT NULL,UNIQUE(text,label)); CREATE TABLE IF NOT EXISTS requests(id INTEGER PRIMARY KEY,text TEXT NOT NULL,prediction TEXT NOT NULL,reviewed_label TEXT,created TEXT NOT NULL);')
    return conn
def examples(conn):
    # Imported/manual examples are curated data. Current request reviews are a
    # separate source of feedback; revising one review cannot delete another.
    return [(r['text'],r['label']) for r in conn.execute('SELECT text,label FROM examples UNION SELECT text,reviewed_label AS label FROM requests WHERE reviewed_label IS NOT NULL')]
def state():
    with connect() as conn:
        counts=Counter(label for _,label in examples(conn))
        training=[{'label':label,'count':count} for label,count in sorted(counts.items())]
        requests=[dict(r) for r in conn.execute('SELECT * FROM requests ORDER BY id DESC LIMIT 100')]
        for r in requests:r['prediction']=json.loads(r['prediction'])
        total=conn.execute('SELECT count(*) FROM requests').fetchone()[0]
    return {'training':training,'requests':requests,'total_requests':total,'training_count':sum(r['count'] for r in training)}
class App(Handler):
    def get_api(self,path):
        if path=='/api/state':return self.send(state())
        if path=='/api/export':
            buff=io.StringIO();writer=csv.writer(buff);writer.writerow(['id','request','suggested_category','model_score','reviewed_category','created'])
            with connect() as conn:
                for r in conn.execute('SELECT * FROM requests ORDER BY id'):
                    pred=json.loads(r['prediction'])
                    safe=lambda v:"'"+v if isinstance(v,str) and v and v[0] in '=+-@\t\r' else v
                    writer.writerow([r['id'],safe(r['text']),safe(pred['label']),pred['score'],safe(r['reviewed_label'] or ''),r['created']])
            return self.send(buff.getvalue(),content_type='text/csv; charset=utf-8',download='request-triage.csv')
        return self.send({'error':'Not found'},404)
    def post_api(self,path,b):
        if path=='/api/train':
            text,label=field(b,'text'),field(b,'label',40)
            with connect() as conn:conn.execute('INSERT OR IGNORE INTO examples(text,label) VALUES(?,?)',(text,label))
            return self.send(state())
        if path=='/api/import':
            reader=csv.DictReader(io.StringIO(field(b,'csv',200000)))
            if not reader.fieldnames or not {'text','label'}<=set(reader.fieldnames):raise ValueError('CSV requires text and label column headers.')
            rows=[]
            for row in reader:
                rows.append((field(row,'text'),field(row,'label',40)))
                if len(rows)>500:raise ValueError('Import at most 500 training examples per batch.')
            if not rows:raise ValueError('The file contains no training examples.')
            with connect() as conn:conn.executemany('INSERT OR IGNORE INTO examples(text,label) VALUES(?,?)',rows)
            return self.send(state())
        if path=='/api/classify':
            text=field(b,'text')
            with connect() as conn:
                result=predict(examples(conn),text)
                cur=conn.execute('INSERT INTO requests(text,prediction,created) VALUES(?,?,?)',(text,json.dumps(result),datetime.now(timezone.utc).isoformat()))
                result['id']=cur.lastrowid
            return self.send(result)
        if path=='/api/review':
            label=field(b,'label',40);key=int(b['id'])
            with connect() as conn:
                row=conn.execute('SELECT text,reviewed_label FROM requests WHERE id=?',(key,)).fetchone()
                if not row:raise ValueError('Request not found.')
                # Keep curated examples immutable here. Training reads the current
                # reviewed label directly, so corrections replace only this request.
                conn.execute('UPDATE requests SET reviewed_label=? WHERE id=?',(label,key))
            return self.send(state())
        return self.send({'error':'Not found'},404)
if __name__=='__main__':serve(App,8101)
