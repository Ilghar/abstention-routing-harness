"""Validate milestone bookkeeping; semantic acceptance still needs review."""
import argparse,json,pathlib

def validate(data,root):
    errors=[];root=pathlib.Path(root).resolve();rows=data.get('milestones',[])
    expected=[f'M{i:02}' for i in range(1,11)]
    if not isinstance(rows,list) or [r.get('id') for r in rows if isinstance(r,dict)]!=expected:
        return ['Milestones must be exactly M01..M10, unique and ordered']
    statuses={'not_started','in_progress','blocked','accepted'};count=0
    for r in rows:
        if r.get('status') not in statuses:errors.append(r['id']+': invalid status')
        if r.get('status')=='accepted':
            count+=1;items=r.get('evidence')
            if not isinstance(items,list) or not items:errors.append(r['id']+': accepted needs artifact evidence');continue
            for entry in items:
                if not isinstance(entry,str):errors.append(r['id']+': invalid evidence path');continue
                p=(root/entry).resolve()
                if not p.is_relative_to(root) or not p.is_file():errors.append(r['id']+': missing/outside artifact '+entry)
    fraction=data.get('completion_fraction')
    if type(fraction) not in (int,float) or fraction!=count/10:errors.append('completion_fraction must equal accepted milestones /10')
    return errors

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('state',type=pathlib.Path);p.add_argument('--root',type=pathlib.Path);a=p.parse_args()
    errors=validate(json.loads(a.state.read_text()),a.root or a.state.resolve().parents[1])
    print(json.dumps({'valid':not errors,'errors':errors,'scope':'bookkeeping only, not semantic or production readiness'}));raise SystemExit(bool(errors))
