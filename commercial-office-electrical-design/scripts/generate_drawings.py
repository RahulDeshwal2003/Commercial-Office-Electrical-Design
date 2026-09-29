"""Generate portable R12 DXF sheets, SVG previews and engineering data.
No CAD library required. Blocks contain simple LINE/CIRCLE/TEXT entities.
Run with Python 3.10+. Output directory is the parent of scripts/.
"""
from pathlib import Path
import json,math,html,collections
from design_data import *
ROOT=Path(__file__).resolve().parents[1]
for d in ['drawings','previews','docs','schedules','calculations']: (ROOT/d).mkdir(exist_ok=True)
LAYERS={
'0':(7,'#22313f',.25),'ARCH-WALLS':(8,'#75818c',.35),'ARCH-DOORS':(8,'#88939d',.18),'ARCH-TEXT':(8,'#64717c',.18),'ARCH-FURNITURE':(8,'#bdc5cb',.15),
'ELEC-LIGHT':(2,'#946308',.3),'ELEC-EMERGENCY':(3,'#197846',.35),'ELEC-SWITCH':(6,'#965385',.25),'ELEC-POWER':(4,'#087a99',.3),'ELEC-DEDICATED':(1,'#b13f38',.35),'ELEC-DB':(1,'#b13f38',.5),'ELEC-CABLE':(5,'#416c9e',.3),'ELEC-SLD':(7,'#22313f',.4),'ELEC-SYMBOLS':(7,'#22313f',.3),'ELEC-TEXT':(7,'#22313f',.18),'ELEC-LIGHT-TEXT':(2,'#946308',.18),'ELEC-DIMENSIONS':(8,'#64717c',.18),'SHEET':(7,'#22313f',.25)}
def pairs(a):return '\n'.join(str(x) for x in a)+'\n'
def entity(typ,layer,a):return [0,typ,8,layer]+a
class Canvas:
    def __init__(self,num,title,scale='NTS'):
        self.num=num;self.title=title;self.scale=scale;self.entities=[];self.svg=[];self.labels=[];self.references=set();self.blocks={}
    def line(self,x,y,X,Y,l='ELEC-SYMBOLS',dash=False):
        if dash:
            n=max(1,math.ceil(math.hypot(X-x,Y-y)/2))
            for i in range(0,n,2):self.line(x+(X-x)*i/n,y+(Y-y)*i/n,x+(X-x)*min(i+1,n)/n,y+(Y-y)*min(i+1,n)/n,l)
            return
        self.entities.append(entity('LINE',l,[10,x,20,420-y,30,0,11,X,21,420-Y,31,0]));co=LAYERS[l]
        self.svg.append(f'<line x1="{x}" y1="{y}" x2="{X}" y2="{Y}" stroke="{co[1]}" stroke-width="{co[2]}"/>')
    def rect(self,x,y,w,h,l='ELEC-SYMBOLS'):
        self.line(x,y,x+w,y,l);self.line(x+w,y,x+w,y+h,l);self.line(x+w,y+h,x,y+h,l);self.line(x,y+h,x,y,l)
    def circle(self,x,y,r,l='ELEC-SYMBOLS'):
        self.entities.append(entity('CIRCLE',l,[10,x,20,420-y,30,0,40,r]));co=LAYERS[l];self.svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{co[1]}" stroke-width="{co[2]}"/>')
    def text(self,x,y,t,h=2.7,l='ELEC-TEXT'):
        t=str(t);self.entities.append(entity('TEXT',l,[10,x,20,420-y,30,0,40,h,1,t,7,'STANDARD',41,.85]));self.labels.append(t)
        self.svg.append(f'<text x="{x}" y="{y}" font-size="{h}" font-family="Arial,sans-serif" fill="{LAYERS[l][1]}">{html.escape(t)}</text>')
    def para(self,x,y,rows,h=2.7,gap=5.2,l='ELEC-TEXT'):
        for i,t in enumerate(rows):self.text(x,y+i*gap,t,h,l)
    def symbol(self,name,x,y,l='ELEC-SYMBOLS',scale=1):
        temp=Canvas('','','');draw_symbol(temp,name,0,0,l)
        # Block coordinates converted from sheet coordinates to local DXF coords.
        if name not in self.blocks:
            ents=[]
            for ent in temp.entities:
                ent=ent.copy();ent[3]='0'
                for j in range(4,len(ent),2):
                    if ent[j] in [20,21]:ent[j+1]-=420
                ents.append(ent)
            self.blocks[name]=ents
        self.entities.append(entity('INSERT',l,[2,name,10,x,20,420-y,30,0,41,scale,42,scale,43,scale]))
        self.svg.append(f'<g transform="translate({x} {y}) scale({scale})">'+''.join(temp.svg)+'</g>')
    def ref(self,c):self.references.add(c)
    def frame(self):
        self.rect(10,10,574,400,'SHEET');self.line(10,48,584,48,'SHEET');self.text(20,26,'NORTHBANK OFFICE',6);self.text(20,39,self.title.upper(),4)
        self.text(456,25,'ELECTRICAL PORTFOLIO',3);self.text(456,34,'CONCEPT DESIGN  /  REV A',2.8);self.text(456,42,'NOT FOR CONSTRUCTION',2.5)
        self.line(10,382,584,382,'SHEET');self.line(345,382,345,410,'SHEET');self.line(480,382,480,410,'SHEET');self.text(18,391,PROJECT,3.1);self.text(18,398,'Designed by: Electrical Engineering Portfolio Project',2.7);self.text(18,405,'Educational exercise; not for construction, certification or regulatory approval.',2.3)
        self.text(353,391,self.num+'  |  '+self.title,2.5);self.text(353,399,'Scale: '+self.scale+' at A2  |  Units: mm',2.5);self.text(488,391,'REV A',3);self.text(488,399,DATE,2.7);self.text(488,406,'Sheet size: 594 x 420 mm',2.3)
    def save(self,stem):
        head=[0,'SECTION',2,'HEADER',9,'$ACADVER',1,'AC1009',9,'$LUNITS',70,2,9,'$LUPREC',70,2,9,'$MEASUREMENT',70,1,9,'$EXTMIN',10,0,20,0,30,0,9,'$EXTMAX',10,594,20,420,30,0,0,'ENDSEC',0,'SECTION',2,'TABLES',0,'TABLE',2,'LTYPE',70,1,0,'LTYPE',2,'CONTINUOUS',70,0,3,'Continuous',72,65,73,0,40,0,0,'ENDTAB',0,'TABLE',2,'LAYER',70,len(LAYERS)]
        for l,(co,_,_) in LAYERS.items():head += [0,'LAYER',2,l,70,0,62,co,6,'CONTINUOUS']
        head += [0,'ENDTAB',0,'TABLE',2,'STYLE',70,1,0,'STYLE',2,'STANDARD',70,0,40,0,41,1,50,0,71,0,42,2.5,3,'standard',4,'',0,'ENDTAB',0,'ENDSEC',0,'SECTION',2,'BLOCKS']
        for name,ents in self.blocks.items():
            head += [0,'BLOCK',8,'0',2,name,70,0,10,0,20,0,30,0,3,name,1,'']
            for ent in ents:head+=ent
            head += [0,'ENDBLK',8,'0']
        head += [0,'ENDSEC',0,'SECTION',2,'ENTITIES']
        for ent in self.entities:head +=ent
        head += [0,'ENDSEC',0,'EOF']
        (ROOT/'drawings'/f'{stem}.dxf').write_text(pairs(head),encoding='ascii')
        (ROOT/'previews'/f'{stem}.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="2376" height="1680" viewBox="0 0 594 420"><rect width="594" height="420" fill="white"/>'+''.join(self.svg)+'</svg>',encoding='utf8')
        return dict(number=self.num,title=self.title,file=stem+'.dxf',entities=len(self.entities),blocks=len(self.blocks),circuits=sorted(self.references),labels=self.labels)
def draw_symbol(c,n,x,y,l):
    if n in ['LP','LB']:
        w=7 if n=='LP' else 8;h=3 if n=='LP' else 1.6;c.rect(x-w/2,y-h/2,w,h,l);c.line(x-w/2,y-h/2,x+w/2,y+h/2,l)
    elif n=='EM':c.circle(x,y,2,l);c.line(x-1.5,y-1.5,x+1.5,y+1.5,l);c.line(x-1.5,y+1.5,x+1.5,y-1.5,l)
    elif n=='EX':c.rect(x-4,y-2,8,4,l);c.text(x-3.1,y+.8,'EXIT',1.7,l)
    elif n in ['SW1','SW2']:
        c.circle(x,y,1.3,l);c.line(x,y-1.3,x+2.5,y-3.5,l)
        if n=='SW2':c.line(x+1,y-.8,x+3.5,y-3,l)
    elif n in ['GPO1','GPO2','DED']:
        c.circle(x,y,1.8,l);c.line(x-2.5,y-2.5,x+2.5,y-2.5,l);c.line(x-.6,y-1,x-.6,y+1,l)
        if n!='GPO1':c.line(x+.6,y-1,x+.6,y+1,l)
        if n=='DED':c.rect(x-3,y-3.5,6,6,l)
    elif n in ['DB','MSB']:
        c.rect(x-4,y-3,8,6,l);c.line(x-4,y-3,x+4,y+3,l)
        if n=='MSB':c.rect(x-5,y-4,10,8,l)
    elif n in ['LOAD1','LOAD3']:
        c.rect(x-4,y-3,8,6,l);c.text(x-2.8,y+1,'3~' if n=='LOAD3' else '1~',2,l)
    elif n=='JUNC':c.circle(x,y,.7,l)
    elif n=='ROUTE':c.line(x-6,y,x+6,y,l,dash=True)
def arrow(c,x,y,X,Y,l='ELEC-CABLE'):
    c.line(x,y,X,Y,l);a=math.atan2(Y-y,X-x)
    for d in [-.5,.5]:c.line(X,Y,X-2*math.cos(a+d),Y-2*math.sin(a+d),l)
def table(c,x,y,widths,headers,rows,h=7.5,font=2.4):
    w=sum(widths);c.rect(x,y,w,h*(len(rows)+1),'SHEET');xx=x
    for col,ww in enumerate(widths):
        if col:c.line(xx,y,xx,y+h*(len(rows)+1),'SHEET')
        c.text(xx+2,y+h*.68,headers[col],font);xx+=ww
    for ri,row in enumerate(rows):
        yy=y+h*(ri+1);c.line(x,yy,x+w,yy,'SHEET');xx=x
        for val,ww in zip(row,widths):c.text(xx+2,yy+h*.68,str(val),font);xx+=ww
def arch(c,f,ox=25,oy=290,scale=75,labels=True):
    k=1000/scale
    def pt(x,y):return ox+x*k,oy-y*k
    def ln(x,y,X,Y,l='ARCH-WALLS'):c.line(*pt(x,y),*pt(X,Y),l)
    def door(x,y,w=.9,up=True):
        ln(x,y,x,y+(w if up else -w),'ARCH-DOORS')
        coords=[(x+w*math.cos(i*math.pi/20),y+(1 if up else -1)*w*math.sin(i*math.pi/20)) for i in range(11)]
        for a,b in zip(coords,coords[1:]):ln(*a,*b,'ARCH-DOORS')
    # Perimeter includes physical exit gaps on GF.
    ln(0,0,0,14);ln(30,0,30,14);ln(0,14,30,14)
    gaps=[(1.5,2.5),(6.4,7.6),(27.5,28.5)] if f=='GF' else []
    prev=0
    for a,b in gaps:ln(prev,0,a,0);door(a,0,b-a,False);prev=b
    ln(prev,0,30,0)
    # Corridor boundaries and northern room partitions. Each room has its own door.
    north=[r for r in ROOMS[f] if r[3]==8]
    for r in north:
        x=r[2];w=r[4];dc=x+w/2-.45
        ln(x,8,dc,8);ln(dc+.9,8,x+w,8);door(dc,8)
        if x>0:ln(x,8,x,14)
    southdoors=[(1.55,2.45),(6.55,7.45),(11.1,12.9),(27.55,28.45)] if f=='GF' else [(1.55,2.45),(7.1,8.9),(22.1,23.9),(27.55,28.45)]
    prev=0
    for a,b in southdoors:ln(prev,6,a,6);door(a,6,b-a,False);prev=b
    ln(prev,6,30,6);ln(4,0,4,6);ln(26,0,26,6)
    if f=='GF':ln(10,0,10,6)
    for xx in [0,26]:
        for yy in [1+i*.32 for i in range(12)]:ln(xx+.5,yy,xx+3.5,yy,'ARCH-FURNITURE')
        arrow(c,*pt(xx+2,1),*pt(xx+2,4.8),'ARCH-DOORS');c.text(*pt(xx+.5,.5),'UP' if f=='GF' else 'DOWN',2,'ARCH-TEXT')
    if labels:
        for r in ROOMS[f]:
            key,name,x,y,w,h=r
            if key=='COR': c.text(*pt(.3,7.8),'CORRIDOR - 2.0 m wide',2.1,'ARCH-TEXT');continue
            c.text(*pt(x+.18,y+h-.3),key,2.1,'ARCH-TEXT')
            if scale==75:c.text(*pt(x+.18,y+h-.63),f'{w*h:.0f} m2',1.8,'ARCH-TEXT')
    # Overall dimensions: values are actual millimetres; model is a plotted sheet.
    x,y=pt(0,15.8);X,Y=pt(30,15.8);c.line(x,y,X,Y,'ELEC-DIMENSIONS');c.text((x+X)/2-8,y-2,'30 000',2.6,'ELEC-DIMENSIONS')
    for xx in [0,30]:c.line(*pt(xx,14.2),*pt(xx,16.1),'ELEC-DIMENSIONS')
    c.text(ox-2,oy+9,f'{f}  /  420 m2  /  1:{scale} at A2',3)
    return pt
def board(c,f,pt):
    xy=(.45,9.7) if f=='GF' else (.4,7.15)
    c.symbol('DB',*pt(*xy),'ELEC-DB');c.text(*pt(xy[0]+.4,xy[1]-.4),'DB-'+f,2.4,'ELEC-DB')
    if f=='GF':c.symbol('MSB',*pt(1,12),'ELEC-DB');c.text(*pt(1.4,11.6),'MSB',2.4,'ELEC-DB')
def side_notes(c,lines):
    c.line(448,60,448,365,'SHEET');c.text(457,68,'DRAWING NOTES',3.3);c.para(457,78,lines,2.6,5.5)
def room_key(c,f,y=319):
    rs=[r for r in ROOMS[f] if r[0]!='COR']
    c.text(25,y,'ROOM KEY',3)
    for i,r in enumerate(rs):c.text(25+(i%3)*139,y+8+(i//3)*6,r[0]+'  '+r[1],2.45)
INDEX=[('E-001','Cover and drawing index','E-001-cover'),('E-002','Symbols and general notes','E-002-symbols'),('E-101','Ground floor lighting','E-101-ground-lighting'),('E-102','First floor lighting','E-102-first-lighting'),('E-201','Ground floor power','E-201-ground-power'),('E-202','First floor power','E-202-first-power'),('E-301','Emergency lighting and exit signs','E-301-emergency-lighting'),('E-401','Main single-line diagram','E-401-single-line-diagram'),('E-501','Distribution board schedules','E-501-panel-schedules'),('E-601','Cable routing and riser','E-601-cable-routing')]
manifest=[]
def finish(c,stem):c.frame();manifest.append(c.save(stem))
def architecture_only():
    c=Canvas('BASE','Architectural design basis','1:75');arch(c,'GF');room_key(c,'GF');side_notes(c,['Ground floor design basis.','All rooms open to corridor.','Two stairs serve both floors.','Reception and waiting are','one open reception suite.','Floor-to-floor: 3.6 m assumed.','Ceiling: 2.8 m assumed.','Architectural / fire / access','review is outside this concept.']);c.frame();c.save('BASE-ground-architecture')
def make_layout(f,lighting):
    idx=INDEX[(2 if f=='GF' else 3) if lighting else (4 if f=='GF' else 5)]
    c=Canvas(idx[0],idx[1],'1:75');pt=arch(c,f);board(c,f,pt)
    if lighting:
        for o in [o for o in lights if o['floor']==f]:
            c.symbol(o['type'],*pt(o['x'],o['y']),'ELEC-LIGHT');c.text(*pt(o['x']-.4,o['y']-.29),o['id'][3:]+'/'+o['circuit'][3:],1.95,'ELEC-LIGHT-TEXT');c.ref(o['circuit'])
        for o in [o for o in switches if o['floor']==f]:
            c.symbol(o['type'],*pt(o['x'],o['y']),'ELEC-SWITCH');c.text(*pt(o['x']+.15,o['y']-.15),o['circuit'][3:],2,'ELEC-LIGHT-TEXT')
        # Representative control connection, not every conductor.
        for s in [s for s in switches if s['floor']==f]:
            target=next((l for l in lights if l['floor']==f and l['room']==s['room'] and l['circuit']==s['circuit']),None)
            if target:c.line(*pt(s['x'],s['y']),*pt(target['x'],target['y']),'ELEC-SWITCH',dash=True)
        cs=[x for x in circuits if x['floor']==f and x['category']=='Lighting']
        c.text(457,165,'LIGHTING CIRCUITS',3.1)
        for i,v in enumerate(cs):
            c.text(457,175+i*14,v['id']+'  '+str(v['w'])+' W',2.7);c.text(457,181+i*14,v['description'],2.25)
        side_notes(c,['LP: 36 W / 4500 lm LED panel.','LB: 24 W / 2800 lm LED batten.','Fixture tag Nxxx takes floor','prefix '+f+' (example '+f+'-N001).','Switch labels show circuit.','See fixture register for mapping.','Dashed lines: control intent.','Switching never interrupts','emergency charge/sense feeds.','Two-way / sensor control at stairs.','Emergency devices on E-301.','Grid is preliminary; see lumen','method in engineering report.'])
        c.text(457,304,'All circuits: 10 A RCBO',2.6);c.text(457,310,'1.5 mm2 Cu + PE (provisional)',2.4)
    else:
        for o in [o for o in outlets if o['floor']==f]:
            c.symbol(o['type'],*pt(o['x'],o['y']),'ELEC-POWER');c.text(*pt(o['x']+.2,o['y']-.25),o['circuit'][3:],2,'ELEC-POWER');c.ref(o['circuit'])
        for o in [o for o in equipment if o['floor']==f]:
            c.symbol('LOAD3' if o['three'] else 'DED',*pt(o['x'],o['y']),'ELEC-DEDICATED');c.text(*pt(o['x']-.3,o['y']-.36),o['circuit'][3:],2.15,'ELEC-DEDICATED');c.ref(o['circuit'])
        # Grouped circuit home-runs along corridor, labels at branch ends.
        c.line(*pt(1,7),*pt(29,7),'ELEC-CABLE',dash=True)
        bx,by=(.45,9.7) if f=='GF' else (.4,7.15)
        c.line(*pt(bx,by),*pt(bx,7),'ELEC-CABLE',dash=True);c.line(*pt(bx,7),*pt(1,7),'ELEC-CABLE',dash=True)
        for x,y,lab in [(12,2.8,'P01'),(18,2.8,'P02'),(24,2.8,'P03'),(13,11,'P04'),(6,5,'P05'),(21 if f=='GF' else 28,11,'P06')]:
            c.line(*pt(x,7),*pt(x,y),'ELEC-CABLE',dash=True)
        side_notes(c,['All circuit tags use floor prefix','('+f+'-P01, '+f+'-REF01, etc.).','Double GPO: two 10 A sockets.','P01-P03: workstation banks.','P04: meeting / office outlets.','P05: reception / copy / cleaning.','P06: kitchen small appliances.','GPO circuits: 20 A RCBO,','4 mm2 Cu + PE provisional.','Dedicated circuits: see E-501','and equipment schedule.','Dashed routes group circuits;','not individual conductor paths.','HVAC units on north service','ledge; local lockable isolators.','No outlets inside wet zones.','Final locations need coordination.'])
        c.text(457,187,'DEDICATED CIRCUITS',3.1)
        eq=[v for v in circuits if v['floor']==f and v['category'] in ['Dedicated','HVAC']]
        for i,v in enumerate(eq):
            c.text(457,197+i*14,v['id']+f"  {v['w']/1000:.2f} kW",2.7);c.text(457,203+i*14,v['description'][:34],2.2)
    room_key(c,f);finish(c,idx[2])
def cover():
    c=Canvas(*INDEX[0][:2]);c.text(25,75,'TWO FLOORS. ONE COORDINATED DESIGN.',5)
    c.para(25,88,['Hypothetical Australian commercial office. 30 m x 14 m per floor.','840 m2 gross floor area. 400/230 V, 3-phase, 50 Hz.','Radial distribution: MSB feeds DB-GF and DB-FF independently.'],3.2,7)
    table(c,25,125,[27,123,65],['DRAWING','TITLE','SCALE AT A2'],[[n,t,'1:75' if n in ['E-101','E-102','E-201','E-202'] else ('1:125 / NTS' if n in ['E-301','E-601'] else 'NTS')] for n,t,_ in INDEX],11,2.8)
    c.text(270,75,'DESIGN SNAPSHOT',4)
    s=summary();c.para(270,90,[f"Connected load: {s['w']/1000:.2f} kW",f"Assumed maximum demand: {s['demand_w']/1000:.2f} kW",f"Conservative apparent demand: {s['demand_va']/1000:.2f} kVA",f"Balanced 3-phase equivalent: {s['current']:.1f} A",f"Highest phase demand: {s['max_current']:.1f} A",'Main protective device: 160 A, 3-pole (provisional)','Floor feeders: 80 A, 3-pole (provisional)'],3.3,9)
    c.text(270,167,'DELIVERABLES',4);c.para(270,180,['10 editable DXF drawing sheets with reusable symbols.','Circuit, equipment, cable and load schedules in CSV.','Traceable load, demand, phase and voltage-drop calculations.','Markdown engineering report and assumptions register.','Python generator and source data for repeatable updates.'],3,8)
    c.text(25,272,'DESIGN BASIS',4);c.para(25,285,['A. All loads, equipment and diversity factors are explicitly assumed.','B. Cable sizes and protection are educational proposals, not certified selections.','C. Final design requires current standards, distributor rules and site verification.','D. Self-contained emergency fittings; no central essential-services board in this scope.','E. Fire systems, lift, PV, EV charging, lightning protection and detailed ICT are excluded.','F. General arrangement includes two stairs; fire separation and accessible access are unresolved.'],3,8)
    c.text(25,349,'READ FIRST',3.5);c.para(25,359,['Start with docs/engineering-report.md and docs/design-assumptions.md.','Use E-002 for symbols and E-501 with the CSV schedules for full circuit details.'],2.8,6)
    finish(c,INDEX[0][2])
def legend():
    c=Canvas(*INDEX[1][:2]);items=[('LP','ELEC-LIGHT','LED panel, 36 W / 4500 lm'),('LB','ELEC-LIGHT','LED batten, 24 W / 2800 lm'),('EM','ELEC-EMERGENCY','Self-contained emergency luminaire'),('EX','ELEC-EMERGENCY','Maintained exit sign, arrow annotated'),('SW1','ELEC-SWITCH','Single switch / local control point'),('SW2','ELEC-SWITCH','Two-gang switch / scene control'),('GPO1','ELEC-POWER','Single socket outlet'),('GPO2','ELEC-POWER','Double general-purpose outlet'),('DED','ELEC-DEDICATED','Dedicated appliance connection'),('DB','ELEC-DB','Floor distribution board'),('MSB','ELEC-DB','Main switchboard'),('LOAD3','ELEC-DEDICATED','Three-phase equipment'),('LOAD1','ELEC-DEDICATED','Single-phase equipment'),('JUNC','ELEC-CABLE','Junction / branch point'),('ROUTE','ELEC-CABLE','Grouped cable route')]
    for i,(s,l,txt) in enumerate(items):c.symbol(s,32,72+i*17,l);c.text(46,73+i*17,s,3);c.text(69,73+i*17,txt,2.8)
    c.text(302,70,'GENERAL NOTES',4)
    c.para(302,82,['01  Concept only. No claim of statutory or standards compliance.','02  Verify applicable NCC edition, jurisdiction and distributor requirements.','03  Review AS/NZS 3000, AS/NZS 3008.1.1, AS/NZS 2293.1,','     AS/NZS 1680 series and AS/NZS 61439 as applicable.','04  Circuit IDs are unique: GF-L01 / FF-P01 / GF-AC01.','05  Equipment AC-GF-01 is served by circuit GF-AC01.','06  Nxxx, SOxxx and Exxx take the floor prefix shown on the sheet.','07  DB-GF and DB-FF are parallel radial feeders from MSB.','08  Separate neutral and PE downstream of the main MEN point.','09  RCD type and compatibility depend on actual equipment.','10  Lighting target: 400 lx office tasks; ancillary targets are assumed.','11  Emergency layout requires photometric / egress verification.','12  Maintain unswitched supply sensing to local emergency fittings.','13  No power-factor correction, harmonic or fault study completed.','14  Paper-space geometry: plans drawn at stated scale in model space.','     Multiply measured plan lengths by 75 or 125 for real mm.','15  Symbols are project conventions; not claimed as standard symbols.'],2.7,8)
    c.text(302,229,'CAD LAYERS',4);c.para(302,241,list(LAYERS.keys())[1:],2.6,6)
    finish(c,INDEX[1][2])
def emergency_sheet():
    c=Canvas(*INDEX[6][:2],'1:125');
    for f,ox in [('GF',25),('FF',315)]:
        pt=arch(c,f,ox,225,125);board(c,f,pt)
        for o in [o for o in emergency if o['floor']==f]:
            c.symbol(o['type'],*pt(o['x'],o['y']),'ELEC-EMERGENCY',.85);c.text(*pt(o['x']+.25,o['y']-.35),o['id'][3:]+'/'+o['circuit'][3:],1.9,'ELEC-EMERGENCY');c.ref(o['circuit'])
            if o['type']=='EX':c.text(*pt(o['x']+.25,o['y']+.5),o['direction'],1.7,'ELEC-EMERGENCY')
        for x,X in [(14,2),(16,28)]:arrow(c,*pt(x,6.5),*pt(X,6.5),'ELEC-EMERGENCY')
        for x in [2,28]:arrow(c,*pt(x,5.7),*pt(x,.5),'ELEC-EMERGENCY')
        c.text(ox,245,f+' emergency fittings: '+str(len([o for o in emergency if o['floor']==f and o['type']=='EM']))+' EM + '+str(len([o for o in emergency if o['floor']==f and o['type']=='EX']))+' EX',3)
    c.text(25,270,'EMERGENCY LIGHTING PHILOSOPHY',3.5);c.para(25,282,['EM: non-maintained self-contained emergency luminaire. EX: maintained self-contained exit sign. Assumed 90-minute battery duration.','Each fitting: 3 W normal input for charging / maintained operation. Load is included ONCE in its local lighting circuit.','Feed upstream of the local wall switch; loss of the local normal lighting supply must initiate emergency operation in that area.','Provide a labelled test facility at each floor DB that simulates supply failure without defeating protective devices.','Arrows indicate conceptual travel direction only. Stair 1 and Stair 2 discharge outdoors at ground level; FF signs direct occupants into stairs.','Emergency fixtures in large open areas and conference room supplement corridor and stair coverage.','Positions, spacing, mounting heights, battery duration and sign viewing distance need AS/NZS 2293.1 and NCC verification.','No lux isolines or product-specific photometry have been calculated. Doors, fire compartments and exit travel distances need architectural review.'],2.8,8)
    finish(c,INDEX[6][2])
def sld():
    c=Canvas(*INDEX[7][:2]);c.text(25,68,'400/230 V  /  3P + N + PE  /  50 Hz',4)
    c.rect(55,78,110,21,'ELEC-SLD');c.para(60,86,['UTILITY LV SUPPLY','Service protection / metering by distributor'],2.5,6);c.line(110,99,110,116,'ELEC-SLD');c.rect(95,116,30,10,'ELEC-SLD');c.text(132,123,'QS-M 200 A main isolator (provisional)',2.7)
    c.line(110,126,110,140,'ELEC-SLD');c.rect(95,140,30,10,'ELEC-SLD');c.text(132,147,'QF-M 160 A 3P MCCB; fault duty TBD',2.7);c.line(110,150,110,163,'ELEC-SLD');c.line(50,163,475,163,'ELEC-SLD');c.text(25,157,'MSB',4);c.text(360,157,'MSB 200 A busbar, full-size neutral',2.6)
    c.text(25,107,'C-M: 4C 70 mm2 Cu + 35 PE, 20 m',2.5)
    for f,x in [('GF',115),('FF',385)]:
        c.line(x,163,x,179,'ELEC-SLD');c.rect(x-15,179,30,10,'ELEC-SLD');c.text(x+20,185,'QF-'+f+' 80 A 3P MCCB',2.6);c.line(x,189,x,215,'ELEC-SLD');c.text(x+7,200,'C-'+f+': 4C 25 + 16 PE Cu',2.5);c.text(x+7,207,'12 m' if f=='GF' else '25 m via riser',2.5);c.rect(x-80,215,230,110,'ELEC-SLD');c.text(x-72,225,'DB-'+f+' 125 A bus / 100 A isolator',3.4)
        cs=[v for v in circuits if v['floor']==f]
        rows=[('L01-L08','8 x 10 A RCBO / 1.5 mm2'),('P01-P06','6 x 20 A RCBO / 4 mm2'),('REF01','10 A RCBO / 2.5 mm2'),('DW01, MW01, WH01, CP01','4 x 16 A RCBO / 2.5 mm2')]
        if f=='GF':rows += [('UPS01 / COM01','16 A / 10 A RCBO, 2.5 mm2')]
        rows += [('AC01 / AC02','2 x 16 A 3P / 4 mm2 + N + PE')]
        for j,(ids,desc) in enumerate(rows):c.text(x-72,237+j*12,ids,2.6);c.text(x-15,237+j*12,desc,2.4)
        for v in cs:c.ref(v['id'])
        su=summary(f);c.text(x-72,318,f"MD {su['demand_w']/1000:.2f} kW; max phase {su['max_current']:.1f} A",2.7)
    c.text(330, seventy:=70,'EARTHING CONCEPT',3.5);c.para(330,82,['Supply PEN / neutral arrangement by distributor.','Main neutral bar -- MEN link -- main earth bar at MSB.','Main earth bar to electrode and equipotential bonding.','PE feeders to DBs; separate N and PE bars downstream.','No downstream N-PE links. Earthing sizes unverified.','Final distributor arrangement and fault-loop design required.'],2.6,6)
    c.para(25,344,['Protection values are provisional. Breaker curves, fault rating and discrimination require a fault-level / coordination study.','30 mA Type A RCBO concept for lighting and socket/appliance final circuits; HVAC/UPS RCD compatibility requires manufacturer review.','No separate mechanical board for four small packaged HVAC units. Self-contained emergency luminaires have no central essential supply.','UPS-01 output feeds SERVER-01 (1.8 kW) and protected ICT (0.2 kW); 2.2 kW input allowance includes losses. Do not add output loads again.'],2.6,7)
    finish(c,INDEX[7][2])
def panels():
    c=Canvas(*INDEX[8][:2]);
    for f,x in [('GF',20),('FF',306)]:
        cs=[v for v in circuits if v['floor']==f];c.text(x,64,'DB-'+f+'  /  80 A feeder  /  125 A bus',3.5)
        rows=[[v['id'][3:],v['description'][:24],v['phase'],f"{v['w']/1000:.2f}",f"{v['current']:.1f}",str(v['breaker']),str(v['cable'])] for v in cs]
        table(c,x,72,[26,85,16,24,24,24,29],['CCT','DESTINATION','PH','kW','A','CB A','mm2'],rows,8.5,2.3)
        y=72+8.5*(len(rows)+1)+10;s=summary(f)
        c.para(x,y,[f"Connected {s['w']/1000:.2f} kW / demand {s['demand_w']/1000:.2f} kW",'Connected phase A / B / C: '+' / '.join(f'{s["phase"][ph]:.1f}' for ph in 'ABC')+' A','Demand phase A / B / C: '+' / '.join(f'{s["md_phase"][ph]:.1f}' for ph in 'ABC')+' A',f"Feeder headroom to highest demand phase: {80-s['max_current']:.1f} A",'Reserve >= 20% physical ways after device module count.'],2.6,6)
        for v in cs:c.ref(v['id'])
    c.para(20,357,['Circuit prefixes: left GF-, right FF-. Current is connected design current; ABC is per-phase current for three-phase equipment.','Sizes are active/neutral Cu conductor areas; PE and complete cable construction are in the cable schedule. CB = proposed protective-device rating.','Full descriptions, destinations, protective-device type, cable lengths and design notes are supplied in schedules/DB-GF.csv and DB-FF.csv.'],2.6,7)
    finish(c,INDEX[8][2])
def cable_sheet():
    c=Canvas(*INDEX[9][:2],'1:125 / NTS')
    for f,ox in [('GF',25),('FF',315)]:
        pt=arch(c,f,ox,221,125);board(c,f,pt)
        c.line(*pt(1,7),*pt(29,7),'ELEC-CABLE',dash=True);c.text(*pt(10,7.5),'TR-'+f+' 150 x 50 tray (concept)',2.4,'ELEC-CABLE')
        for x,y in [(2,12),(5,11),(12,11),(16,11),(22,11),(28,11),(12,3),(20,3)]:c.line(*pt(x,7),*pt(x,y),'ELEC-CABLE',dash=True)
        for o in [o for o in equipment if o['floor']==f]:
            c.symbol('LOAD3' if o['three'] else 'DED',*pt(o['x'],o['y']),'ELEC-DEDICATED',.7);c.line(*pt(o['x'],7),*pt(o['x'],o['y']),'ELEC-CABLE',dash=True);c.ref(o['circuit'])
        c.symbol('JUNC',*pt(1,7),'ELEC-CABLE');c.text(*pt(1.5,6.3),'R1 RISER',2.5,'ELEC-CABLE')
        if f=='GF':
            c.line(*pt(1,12),*pt(.45,12),'ELEC-CABLE');c.line(*pt(.45,12),*pt(.45,9.7),'ELEC-CABLE');c.text(*pt(1.4,10.5),'C-GF',2.5)
            c.line(*pt(1,12),*pt(1,7),'ELEC-CABLE');c.line(*pt(.45,9.7),*pt(.45,7),'ELEC-CABLE',dash=True);c.line(*pt(.45,7),*pt(1,7),'ELEC-CABLE',dash=True)
        else:c.line(*pt(.4,7.15),*pt(1,7),'ELEC-CABLE')
    c.text(25,255,'VERTICAL RISER R1 - NOT TO SCALE',3.5);c.line(25,286,260,286,'ARCH-WALLS');c.line(25,330,260,330,'ARCH-WALLS');c.text(25,282,'FIRST FLOOR +3.6 m',2.7);c.text(25,326,'GROUND FLOOR +0.0 m',2.7)
    c.rect(70,305,30,12,'ELEC-DB');c.text(75,313,'MSB',3);c.rect(165,305,32,12,'ELEC-DB');c.text(168,313,'DB-GF',2.7);c.rect(165,264,32,12,'ELEC-DB');c.text(168,272,'DB-FF',2.7);c.line(100,311,165,311,'ELEC-CABLE');c.text(113,307,'C-GF 12 m',2.5);c.line(85,305,85,270,'ELEC-CABLE');c.line(85,270,165,270,'ELEC-CABLE');c.text(94,266,'C-FF 25 m',2.5)
    c.para(290,257,['Both feeders originate at MSB; DB-FF is not fed through DB-GF.','C-M: 4C 70 + 35 PE Cu, 20 m assumed underground/service route.','C-GF / C-FF: 4C 25 + 16 PE Cu, tray / riser concept.','All lengths include routing and termination allowance; verify on site.','Tray dimensions are spatial allowances, not fill-capacity calculations.','Branch conduits segregate power from ICT/data; avoid wet-service zones.','Provide suitable supports, bend radii, fire-stopping and access.','No fire-rated circuit claim. Coordinate penetration systems and riser.','Final circuits have individual neutrals and PE; no shared neutrals.','Typical final lengths: lighting 35-45 m; GPO 45 m; equipment 20-45 m.'],2.65,8)
    finish(c,INDEX[9][2])
def main():
    import sys
    if '--architecture-only' in sys.argv:architecture_only();return
    cover();legend()
    for f in ['GF','FF']:make_layout(f,True)
    for f in ['GF','FF']:make_layout(f,False)
    emergency_sheet();sld();panels();cable_sheet()
    (ROOT/'scripts'/'model.json').write_text(json.dumps(MODEL,indent=2))
    (ROOT/'docs'/'drawing-manifest.json').write_text(json.dumps(manifest,indent=2))
    print(json.dumps(MODEL['summaries'],indent=2));print('Generated',len(manifest),'sheets')
if __name__=='__main__':main()
