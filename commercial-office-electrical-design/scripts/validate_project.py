"""Independent structural DXF and cross-file engineering checks (not certification)."""
from pathlib import Path
import csv,json,math
from design_data import *
R=Path(__file__).resolve().parents[1]; checks=[]
def check(ok,msg):
    if not ok:raise AssertionError(msg)
    checks.append(msg)
def readcsv(p):
    with (R/p).open(newline='',encoding='utf8') as f:return list(csv.DictReader(f))
ids={c['id'] for c in circuits};check(len(ids)==len(circuits),'All 44 circuit IDs unique')
for f in ['GF','FF']:
    check(sum(r[4]*r[5] for r in ROOMS[f])==420,f+' room areas reconcile to 420 m2')
    rows=readcsv('schedules/DB-'+f+'.csv');cs=[c for c in circuits if c['floor']==f]
    check({r['Circuit'] for r in rows}=={c['id'] for c in cs},f+' board CSV includes every circuit exactly once')
    check(len(rows)==len(cs),f+' board CSV has no duplicates')
    for r in rows:
        c=next(c for c in cs if c['id']==r['Circuit']);check(abs(float(r['Load_W'])-c['w'])<.001 and r['Phase']==c['phase'],r['Circuit']+' schedule agrees with input model')
    actual=sum(float(r['Load_W']) for r in rows);check(abs(actual-summary(f)['w'])<.001,f+' load total reconciles')
for c in circuits:
    check(c['current']<=c['breaker'],c['id']+' connected design current below device rating')
    if c['category']=='Lighting':check(sum(l['w'] for l in lights+emergency if l['circuit']==c['id'])==c['w'],c['id']+' normal + emergency load reconciles')
for coll in [lights,outlets,equipment,emergency,switches]:
    for o in coll:check(o['circuit'] in ids,o['id']+' has valid circuit')
    check(len({o['id'] for o in coll})==len(coll),'Device register has unique IDs')
manifest=json.loads((R/'docs/drawing-manifest.json').read_text());check(len(manifest)==10,'Ten indexed E-series DXF sheets')
for sheet in manifest:
    p=R/'drawings'/sheet['file'];lines=p.read_text().splitlines();check(len(lines)%2==0,p.name+' balanced DXF group/value pairs')
    pairs=[(int(lines[i]),lines[i+1]) for i in range(0,len(lines),2)];check(pairs[-1]==(0,'EOF'),p.name+' EOF marker')
    # Parse DXF entities independently of generator object state.
    ents=[];cur=[]
    for code,value in pairs:
        if code==0:
            if cur:ents.append(cur)
            cur=[(code,value)]
        else:cur.append((code,value))
    if cur:ents.append(cur)
    blocks={dict(e).get(2) for e in ents if e[0][1]=='BLOCK'}
    inserts=[dict(e).get(2) for e in ents if e[0][1]=='INSERT'];check(set(inserts)<=blocks,p.name+' INSERT references resolve to blocks')
    check(set(sheet['circuits'])<=ids,p.name+' circuit references resolve')
    check(sheet['number'] in [dict(e).get(1,'').split('  |')[0] for e in ents if e[0][1]=='TEXT'],p.name+' title block drawing ID')
    check(all(not any(t in e[0][1] for t in ['PROXY','3DSOLID','ACAD_TABLE']) for e in ents),p.name+' no proprietary proxy/3D entities')
    check(any(k==1 and v=='NOT FOR CONSTRUCTION' for k,v in pairs),p.name+' concept status present')
for number in ['E-401','E-501']:check(set(next(s for s in manifest if s['number']==number)['circuits'])==ids,number+' includes every circuit')
for f,num in [('GF','E-101'),('FF','E-102')]:check(set(next(s for s in manifest if s['number']==num)['circuits'])=={c['id'] for c in circuits if c['floor']==f and c['category']=='Lighting'},num+' includes all lighting circuits')
for f,num in [('GF','E-201'),('FF','E-202')]:check(set(next(s for s in manifest if s['number']==num)['circuits'])=={c['id'] for c in circuits if c['floor']==f and c['category']!='Lighting'},num+' includes all power/equipment circuits')
rows=readcsv('calculations/cable-sizing.csv')
for r in rows:
    check(float(r['Ib_A'])<=float(r['In_A'])<=float(r['Illustrative_Iz_A']),r['Circuit']+' illustrative current-capacity screen')
    check(float(r['Accumulated_drop_percent'])<5,r['Circuit']+' resistance-only path drop below internal 5% target')
loads=readcsv('schedules/load-schedule.csv');check(sum(float(r['Connected_W']) for r in loads)==summary()['w'],'CSV building connected load reconciles')
check(abs(sum(float(r['Demand_W']) for r in loads)-summary()['demand_w'])<.001,'CSV building demand reconciles')
for r in readcsv('calculations/lighting-lumen-method.csv'):
    val=float(r['Total_lm'])*float(r['Assumed_UF'])*float(r['Assumed_MF'])/float(r['Area_m2']);check(abs(val-float(r['Estimated_average_lx']))<.06,r['Floor']+' '+r['Room']+' lumen calculation checked')
result={'status':'passed','checks':len(checks),'circuits':len(circuits),'normal_luminaires':len(lights),'emergency_and_exit_fittings':len(emergency),'double_outlets':len(outlets),'equipment_connections':len(equipment),'connected_W':summary()['w'],'demand_W':summary()['demand_w'],'maximum_phase_demand_A':summary()['max_current'],'max_drop_percent':max(float(r['Accumulated_drop_percent']) for r in rows),'scope':'Structural and numerical consistency only; not standards compliance'}
(R/'docs/validation-results.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
