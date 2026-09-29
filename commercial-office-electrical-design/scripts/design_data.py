"""Authoritative conceptual inputs. Units: metres, watts, volts, amperes."""
from math import sqrt
DATE='2026-09-29'
PROJECT='Two-Storey Commercial Office Electrical Design'
ROOMS={
'GF': [('ELEC','Electrical',0,8,3,6),('COM','Communications',3,8,3,6),('STO','Storage',6,8,2,6),('ACC','Accessible WC',8,8,2,6),('MT1','Meeting 1',10,8,4,6),('MT2','Meeting 2',14,8,4,6),('KIT','Kitchen / break',18,8,6,6),('M WC','Male WC',24,8,3,6),('F WC','Female WC',27,8,3,6),('ST1','Stair 1',0,0,4,6),('REC','Reception',4,0,6,3),('WAIT','Waiting',4,3,6,3),('OPEN','Open office',10,0,16,6),('ST2','Stair 2',26,0,4,6),('COR','Corridor',0,6,30,2)],
'FF': [('PRT','Print / copy',0,8,3,6),('STO','Storage',3,8,2,6),('ACC','Accessible WC',5,8,3,6),('WC','Toilets',8,8,3,6),('CONF','Conference',11,8,6,6),('MT1','Small meeting',17,8,4,6),('MGR1','Manager 1',21,8,3,6),('MGR2','Manager 2',24,8,3,6),('KIT','Kitchen / break',27,8,3,6),('ST1','Stair 1',0,0,4,6),('OPEN','Open office',4,0,22,6),('ST2','Stair 2',26,0,4,6),('COR','Corridor',0,6,30,2)]}
circuits=[]; lights=[]; outlets=[]; equipment=[]; emergency=[]; switches=[]
def circuit(f,s,desc,w,cat='Lighting',pf=.95,div=1,breaker=10,cable=1.5,length=35,three=False,dest='',notes=''):
    c=dict(id=f+'-'+s,board='DB-'+f,floor=f,description=desc,w=w,category=cat,pf=pf,diversity=div,breaker=breaker,cable=cable,length=length,three=three,destination=dest or desc,notes=notes)
    c['current']=w/((sqrt(3)*400 if three else 230)*pf);c['demand_w']=w*div;c['demand_va']=w*div/pf;circuits.append(c);return c
def room(f,k): return next(r for r in ROOMS[f] if r[0]==k)
def grid(f,k,nx,ny,s,typ='LP'):
    r=room(f,k); _,_,x,y,w,h=r
    for j in range(ny):
        for i in range(nx):
            xx=x+w*(i+.5)/nx; yy=y+h*(j+.5)/ny
            lights.append(dict(floor=f,room=k,x=xx,y=yy,circuit=f+'-'+s,type=typ,w=36 if typ=='LP' else 24,lm=4500 if typ=='LP' else 2800))
def sw(f,k,s,double=False):
    r=room(f,k);x=r[2]+.35;y=8.3 if r[3]==8 else 5.65
    switches.append(dict(floor=f,room=k,x=x,y=y,circuit=f+'-'+s,type='SW2' if double else 'SW1'))
# L01/L02 divide open office into alternating north/south rows.
for f in ['GF','FF']:
    r=room(f,'OPEN');nx=8 if f=='GF' else 11
    for j in range(3):
        for i in range(nx):
            lights.append(dict(floor=f,room='OPEN',x=r[2]+r[4]*(i+.5)/nx,y=1+j*2,circuit=f+'-'+('L01' if i<nx//2 else 'L02'),type='LP',w=36,lm=4500))
    sw(f,'OPEN','L01',True); switches.append(dict(floor=f,room='OPEN',x=r[2]+r[4]-.4,y=5.65,circuit=f+'-L02',type='SW2'))
    for k,nx,ny,s,typ in ([('REC',2,2,'L03','LP'),('WAIT',2,2,'L03','LP'),('MT1',2,3,'L04','LP'),('MT2',2,3,'L04','LP'),('KIT',3,3,'L05','LP'),('M WC',1,3,'L05','LB'),('F WC',1,3,'L05','LB'),('ACC',1,2,'L05','LB'),('ELEC',1,3,'L06','LB'),('COM',1,3,'L06','LB'),('STO',1,2,'L06','LB')] if f=='GF' else [('CONF',3,3,'L03','LP'),('MT1',2,3,'L03','LP'),('MGR1',2,2,'L04','LP'),('MGR2',2,2,'L04','LP'),('KIT',1,3,'L05','LP'),('WC',1,3,'L05','LB'),('ACC',1,3,'L05','LB'),('PRT',1,3,'L06','LP'),('STO',1,2,'L06','LB')]):
        grid(f,k,nx,ny,s,typ);sw(f,k,s)
    grid(f,'COR',10,1,'L07','LB');grid(f,'ST1',1,3,'L08','LB');grid(f,'ST2',1,3,'L08','LB')
    switches += [dict(floor=f,room='COR',x=1,y=6.3,circuit=f+'-L07',type='SW1'),dict(floor=f,room='ST1',x=.5,y=5.6,circuit=f+'-L08',type='SW1'),dict(floor=f,room='ST2',x=26.5,y=5.6,circuit=f+'-L08',type='SW1')]
    # Emergency fixtures use unswitched local lighting feeds, not a remote unmonitored circuit.
    points=[(2,7,'L07'),(7,7,'L07'),(12,7,'L07'),(17,7,'L07'),(22,7,'L07'),(28,7,'L07'),(2,1,'L08'),(2,4.5,'L08'),(28,1,'L08'),(28,4.5,'L08')]
    points += ([(12,3,'L01'),(18,3,'L02'),(24,3,'L02'),(7,1.3,'L03')] if f=='GF' else [(6,3,'L01'),(12,3,'L01'),(18,3,'L02'),(24,3,'L02'),(14,11,'L03')])
    for x,y,s in points: emergency.append(dict(floor=f,type='EM',x=x,y=y,circuit=f+'-'+s,w=3))
    xp=[(2,6,'L08','DOWN'),(28,6,'L08','DOWN'),(8,7,'L07','LEFT'),(23,7,'L07','RIGHT')]
    if f=='GF':xp += [(2,0,'L08','OUT'),(28,0,'L08','OUT'),(7,0,'L03','OUT')]
    for x,y,s,d in xp:emergency.append(dict(floor=f,type='EX',x=x,y=y,circuit=f+'-'+s,w=3,direction=d))
    for i in range(1,9):
        s=f'L{i:02}';n=[l for l in lights if l['circuit']==f+'-'+s];em=[e for e in emergency if e['circuit']==f+'-'+s]
        circuit(f,s,{'L01':'Open office west','L02':'Open office east','L03':'Reception / waiting' if f=='GF' else 'Conference / meeting','L04':'Meeting rooms' if f=='GF' else 'Manager offices','L05':'Kitchen / toilets','L06':'Service rooms','L07':'Corridor','L08':'Both stairs'}[s],sum(l['w'] for l in n)+sum(e['w'] for e in em),length=45 if i==8 else 35,notes=f'{len(n)} normal + {len(em)} EM/EX; unswitched emergency tap')
    # Six general outlet circuits, diversity applies to assumed equipment demand, not socket ratings.
    groups=[('P01','Desk bank west',[(6 if f=='FF' else 11,1.7),(8 if f=='FF' else 13,1.7),(10 if f=='FF' else 15,1.7),(6 if f=='FF' else 11,4.3),(8 if f=='FF' else 13,4.3),(10 if f=='FF' else 15,4.3)]),('P02','Desk bank centre',[(16,1.7),(18,1.7),(20,1.7),(16,4.3),(18,4.3),(20,4.3)]),('P03','Desk bank east',[(21,1.7),(23,1.7),(25,1.7),(21,4.3),(23,4.3),(25,4.3)]),('P04','Meeting / offices',[(11,8.6),(13,13.4),(15,8.6),(17,13.4)] if f=='GF' else [(12,8.6),(16,13.4),(18,8.6),(20,13.4),(22,8.6),(25,8.6)]),('P05','Reception / cleaning' if f=='GF' else 'Print / cleaning',[(4.5,1),(9.5,4.5),(5,6.4),(15,6.4),(25,6.4)] if f=='GF' else [(1,8.6),(2,13.4),(5,6.4),(15,6.4),(25,6.4)]),('P06','Kitchen small power',[(19,13.4),(20.5,13.4),(22,13.4)] if f=='GF' else [(27.5,13.4),(28.5,13.4),(29.5,13.4)])]
    for s,desc,pts in groups:
        for x,y in pts:outlets.append(dict(floor=f,x=x,y=y,circuit=f+'-'+s,type='GPO2',room=desc))
        watts=2400 if s in ['P01','P02','P03'] else (3000 if s=='P06' else 1800)
        circuit(f,s,desc,watts,'General power',.95,.6,20,4,45,notes=f'{len(pts)} double GPO; estimated equipment load')
    # Dedicated appliance powers are electrical input, including HVAC.
    eq=[('REF01','Refrigerator',250,.9,.8,10,2.5,25,19 if f=='GF' else 27.5,12.5),('DW01','Dishwasher',2000,1,.8,16,2.5,30,21 if f=='GF' else 28.5,12),('MW01','Microwave',1500,.95,.8,16,2.5,30,23 if f=='GF' else 29.5,12.5),('WH01','Storage water heater',2400,1,1,16,2.5,30,23 if f=='GF' else 29,9),('CP01','Copier',1500,.95,.6,16,2.5,30,9 if f=='GF' else 1.5,5 if f=='GF' else 11)]
    if f=='GF': eq += [('UPS01','UPS-01 input / server rack',2200,.95,1,16,2.5,20,4.5,11),('COM01','Comms equipment non-UPS',400,.95,1,10,2.5,20,5.5,9.5)]
    for s,desc,w,pf,d,b,ca,le,x,y in eq:
        c=circuit(f,s,desc,w,'Dedicated',pf,d,b,ca,le,notes='30 mA Type A RCBO; manufacturer verification')
        equipment.append(dict(id=f+'-'+s,circuit=c['id'],floor=f,x=x,y=y,description=desc,three=False))
    for i,(x,y) in enumerate([(11,14.8),(22,14.8)],1):
        s=f'AC{i:02}';c=circuit(f,s,f'AC-{f}-{i:02} packaged HVAC',6000,'HVAC',.9,.9,16,4,45,True,notes='3P protection; RCD type per inverter manufacturer; local isolator')
        equipment.append(dict(id=f'AC-{f}-{i:02}',circuit=c['id'],floor=f,x=x,y=y,description='HVAC outdoor unit',three=True))
# Global numbering and connected-current phase balancing by floor.
for f in ['GF','FF']:
    totals=[0.,0.,0.]
    for c in sorted([c for c in circuits if c['floor']==f and not c['three']],key=lambda c:-c['current']):
        phase=min(range(3),key=lambda i:totals[i]);c['phase']='ABC'[phase];totals[phase]+=c['current']
    for c in circuits:
        if c['floor']==f and c['three']:c['phase']='ABC'
# Rotate FF B/C to reduce aggregate maximum-demand imbalance at the MSB.
for c in circuits:
    if c['floor']=='FF' and not c['three']: c['phase']={'A':'A','B':'C','C':'B'}[c['phase']]
for coll,pref in [(lights,'N'),(outlets,'SO'),(emergency,'E'),(switches,'S')]:
    for f in ['GF','FF']:
        for i,o in enumerate([x for x in coll if x['floor']==f],1):o['id']=f+'-'+pref+f'{i:03}'
def summary(f=None):
    cs=[c for c in circuits if f is None or c['floor']==f]
    p=sum(c['w'] for c in cs); pd=sum(c['demand_w'] for c in cs);s=sum(c['demand_va'] for c in cs)
    phase={ph:sum((c['current']/1 if c['three'] or c['phase']==ph else 0) for c in cs) for ph in 'ABC'}
    md={ph:sum((c['current']*c['diversity'] if c['three'] or c['phase']==ph else 0) for c in cs) for ph in 'ABC'}
    return dict(w=p,demand_w=pd,demand_va=s,pf=pd/s,current=s/(sqrt(3)*400),phase=phase,md_phase=md,max_current=max(md.values()),rating=80 if f else 160)
MODEL=dict(rooms=ROOMS,circuits=circuits,lights=lights,outlets=outlets,equipment=equipment,emergency=emergency,switches=switches,summaries={f:summary(f) for f in ['GF','FF']})
MODEL['summaries']['MSB']=summary()
