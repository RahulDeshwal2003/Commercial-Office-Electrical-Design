"""Engineering analysis and documentation; CSV table data exported through export_schedules.mjs."""
from pathlib import Path
from math import sqrt
from collections import defaultdict
import json
from design_data import *
R=Path(__file__).resolve().parents[1]; tables={}
def write(p,t):(R/p).write_text(t,encoding='utf8')
def md(headers,rows):return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(map(str,r))+' |' for r in rows)+'\n'
def tab(path,heads,rows):tables[path]=[heads]+rows
def protection(c):return ('3P MCB; RCD per manufacturer' if c['three'] else '1P+N 30mA Type A RCBO')
def cab(c):return f"{'4C' if c['three'] else '2C'} {c['cable']} mm2 Cu + {c['cable'] if c['cable']<=4 else 4} mm2 PE"
for f in ['GF','FF']:
    tab('schedules/DB-'+f+'.csv',['Circuit','Description','Phase','Load_W','PF','Design_current_A','Breaker_A','Protection','Cable','Destination','Length_m','Diversity','Demand_W','Notes'],[[c['id'],c['description'],c['phase'],c['w'],c['pf'],round(c['current'],3),c['breaker'],protection(c),cab(c),c['destination'],c['length'],c['diversity'],c['demand_w'],c['notes']] for c in circuits if c['floor']==f])
eqrows=[]
for e in equipment:
    c=next(c for c in circuits if c['id']==e['circuit']);eqrows.append([e['id'],c['id'],e['description'],c['w'],'400 V 3P+N+PE' if c['three'] else '230 V 1P+N+PE',c['pf'],round(c['current'],3),c['breaker'],protection(c),cab(c),e['floor'],e['x'],e['y'],'Estimated electrical input; verify nameplate'])
tab('schedules/equipment-schedule.csv',['Equipment_ID','Circuit','Description','Input_W','Supply','PF','Current_A','Breaker_A','Protection','Cable','Floor','X_m','Y_m','Basis'],eqrows)
tab('schedules/fixture-register.csv',['Tag','Floor','Room','Type','Circuit','Input_W','Lumens','X_m','Y_m'],[[o['id'],o['floor'],o['room'],o['type'],o['circuit'],o['w'],o['lm'],round(o['x'],3),round(o['y'],3)] for o in lights])
tab('schedules/emergency-register.csv',['Tag','Floor','Type','Circuit','Normal_input_W','Direction','X_m','Y_m','Battery_min','Control'],[[o['id'],o['floor'],o['type'],o['circuit'],o['w'],o.get('direction','NA'),o['x'],o['y'],90,'Unswitched local lighting circuit; simulate failure for test'] for o in emergency])
tab('schedules/outlet-register.csv',['Tag','Floor','Type','Circuit','Area','X_m','Y_m'],[[o['id'],o['floor'],o['type'],o['circuit'],o['room'],o['x'],o['y']] for o in outlets])
tab('schedules/load-schedule.csv',['Circuit','Category','Connected_W','PF','Demand_factor','Demand_W','Demand_VA','Phase'],[[c['id'],c['category'],c['w'],c['pf'],c['diversity'],c['demand_w'],round(c['demand_va'],3),c['phase']] for c in circuits])
loadrows=[]
for f in ['GF','FF']:
    for cat in ['Lighting','General power','Dedicated','HVAC']:
        cs=[c for c in circuits if c['floor']==f and c['category']==cat];loadrows.append([f,cat,sum(c['w'] for c in cs),sum(c['demand_w'] for c in cs),round(sum(c['demand_va'] for c in cs),3)])
tab('calculations/electrical-loads.csv',['Board_floor','Category','Connected_W','Demand_W','Demand_VA'],loadrows)
phaserows=[]
for f in ['GF','FF','MSB']:
    s=summary(None if f=='MSB' else f)
    for ph in 'ABC':phaserows.append([f,ph,round(s['phase'][ph],3),round(s['md_phase'][ph],3),s['rating'],round(s['rating']-s['md_phase'][ph],3)])
tab('calculations/phase-balancing.csv',['Board','Phase','Connected_A','Demand_A','Upstream_breaker_A','Demand_headroom_A'],phaserows)
# All Iz inputs are deliberately illustrative placeholders, not extracted standard ratings.
IZ={1.5:18,2.5:25,4:34,25:125,70:220};factor=.8;rho=.0225
def cable_row(cid,board,A,PE,I,In,L,three,role):
    v=400 if three else 230;dv=(sqrt(3) if three else 2)*rho*L*I/A
    return dict(id=cid,board=board,area=A,pe=PE,Ib=I,In=In,length=L,three=three,v=v,baseIz=IZ[A],factor=factor,Iz=IZ[A]*factor,dv=dv,pct=dv/v*100,role=role)
cables=[cable_row('C-M','MSB',70,35,summary()['max_current'],160,20,True,'Incoming'),cable_row('C-GF','DB-GF',25,16,summary('GF')['max_current'],80,12,True,'Feeder'),cable_row('C-FF','DB-FF',25,16,summary('FF')['max_current'],80,25,True,'Feeder')]
for c in circuits:cables.append(cable_row(c['id'],c['board'],c['cable'],c['cable'],c['current'],c['breaker'],c['length'],c['three'],'Final'))
for ca in cables:
    if ca['role']=='Incoming': ca['total_pct']=ca['pct']
    elif ca['role']=='Feeder':ca['total_pct']=cables[0]['pct']+ca['pct']
    else:
        feed=next(x for x in cables if x['id']==('C-GF' if ca['board']=='DB-GF' else 'C-FF'));ca['total_pct']=cables[0]['pct']+feed['pct']+ca['pct']
tab('schedules/cable-schedule.csv',['Cable_ID','Board','Role','Cores','Active_neutral_mm2','PE_mm2','Length_m','Route','Proposed_In_A'],[[c['id'],c['board'],c['role'],4 if c['three'] else 2,c['area'],c['pe'],c['length'],'Service' if c['role']=='Incoming' else ('Tray/riser' if c['role']=='Feeder' else 'Tray + conduit'),c['In']] for c in cables])
tab('calculations/cable-sizing.csv',['Circuit','Ib_A','In_A','Assumed_base_Iz_A','Derating_factor','Illustrative_Iz_A','Area_mm2','Length_m','Voltage_V','Drop_V','Drop_percent','Accumulated_drop_percent','Ib_le_In_le_Iz','Basis'],[[c['id'],round(c['Ib'],3),c['In'],c['baseIz'],c['factor'],c['Iz'],c['area'],c['length'],c['v'],round(c['dv'],4),round(c['pct'],4),round(c['total_pct'],4),c['Ib']<=c['In']<=c['Iz'],'Illustrative Iz only; resistive drop at rho=0.0225; no reactance'] for c in cables])
lumen=[]
for f in ['GF','FF']:
    for r in ROOMS[f]:
        k,name,x,y,w,h=r;ls=[o for o in lights if o['floor']==f and o['room']==k];uf=.5 if k=='COR' else (.6 if k in ['ST1','ST2','ACC','WC','M WC','F WC','ELEC','STO','COM'] else .65);target=100 if k=='COR' else (150 if k in ['ST1','ST2'] else (200 if uf==.6 else 400));E=sum(o['lm'] for o in ls)*uf*.8/(w*h)
        lumen.append([f,k,name,w*h,len(ls),sum(o['w'] for o in ls),sum(o['lm'] for o in ls),uf,.8,target,round(E,1)])
tab('calculations/lighting-lumen-method.csv',['Floor','Room','Name','Area_m2','Count','Input_W','Total_lm','Assumed_UF','Assumed_MF','Target_lx','Estimated_average_lx'],lumen)
write('scripts/schedule-data.json',json.dumps(tables,indent=2))
write('scripts/cable-model.json',json.dumps(cables,indent=2))
S=summary();GF=summary('GF');FF=summary('FF')
summary_table=md(['Board','Connected kW','Demand kW','Demand kVA','Equivalent A','Highest phase A','Breaker A'],[[f,f'{s["w"]/1000:.3f}',f'{s["demand_w"]/1000:.3f}',f'{s["demand_va"]/1000:.3f}',f'{s["current"]:.2f}',f'{s["max_current"]:.2f}',s['rating']] for f,s in [('DB-GF',GF),('DB-FF',FF),('MSB',S)]])
cable_examples=['C-M','C-GF','C-FF','GF-L01','GF-P01','GF-UPS01','GF-AC01']
cabletable=md(['Circuit','Ib A','In A','Cu mm2','Length m','Assumed derated Iz A','Drop %','Total path %'],[[c['id'],f'{c["Ib"]:.2f}',c['In'],c['area'],c['length'],c['Iz'],f'{c["pct"]:.2f}',f'{c["total_pct"]:.2f}'] for c in cables if c['id'] in cable_examples])
sources='''## Reference framework

- [NSW Fair Trading: electrical standards, rules and notes](https://www.fairtrading.nsw.gov.au/trades-and-businesses/construction-and-trade-essentials/electricians/standards-rules-and-notes) identifies the Wiring Rules as an installation safety reference.
- [ABCB: NCC 2022 Part E4](https://ncc.abcb.gov.au/editions/ncc-2022/adopted/volume-one/e-services-and-equipment/part-e4-visibility-emergency-exit-signs-and-warning-systems) describes emergency visibility, exit identification and the AS/NZS 2293.1 framework.

These public references were checked on 29 September 2026 for context, not to certify current project applicability. NCC 2022 is a reference edition, not an assertion of the edition adopted in a particular jurisdiction on the design date. Obtain current adopted NCC provisions, amendments, distributor service rules and licensed copies of applicable AS/NZS 3000, 3008.1.1, 2293.1, 1680 and 61439 requirements before detailed design. No standard tables or mandatory lux values have been reproduced or claimed as verified.
'''
write('docs/design-assumptions.md','''# Design assumptions - Revision A

This is a fictional project. Numerical values below are assumptions, not measured site data.

| Item | Basis |
| --- | --- |
| Building | Class 5 office concept; 30 x 14 m gross per floor, 420 m2 each, 840 m2 total |
| Architectural envelope | Wall centreline areas; internal partition thickness not deducted |
| Occupancy | Approximately 50 people total; no occupancy-code calculation |
| Levels | GF +0.0 m, FF +3.6 m; ceiling 2.8 m; task plane 0.8 m |
| Escape | Two conceptual stairs; GF doors discharge outdoors; fire separation and travel distances unverified |
| Access | Accessible toilet on both levels; accessible inter-floor access/lift design excluded and unresolved |
| Electrical | 400/230 V, 50 Hz, three-phase LV; 400 and 230 are nominal, not exact sqrt(3) multiples |
| Earthing | Australian MEN/TN-C-S concept at MSB; separate N and PE downstream; distributor arrangement unverified |
| Fault level | Unknown. Breaking capacity, selectivity and fault-loop compliance not established |
| Distribution | MSB has separate radial feeders to DB-GF and DB-FF |
| Main / feeder | 160 A MSB protection, 80 A floor feeders; ratings are provisional |
| Lighting | LP 36 W/4500 lm; LB 24 W/2800 lm; UF 0.50-0.65, MF 0.80 |
| Lighting targets | Assumed 400 lx offices/meeting/kitchens, 200 lx service/toilets, 150 lx stairs, 100 lx corridor |
| Emergency | Self-contained EM and maintained EX, 3 W input each, assumed 90-minute battery |
| GPO load | Workstation circuit 2.4 kW, other general circuit 1.8 kW, kitchen circuit 3.0 kW; not socket rated capacity |
| Equipment | Appliance powers are nameplate estimates; HVAC 6 kW electrical input per unit, four total |
| Server | SERVER-01 1.8 kW + protected ICT 0.2 kW downstream of UPS-01; 2.2 kW UPS input includes losses |
| Comms | Separate 0.4 kW non-UPS circuit; no double-count with protected ICT |
| PF | Lighting/general/most appliances 0.95; resistive heaters/dishwashers 1; fridge/HVAC 0.90 |
| Demand factors | Lighting 1; general power 0.6; fridge/DW/MW 0.8; copier 0.6; water heater/server/comms 1; HVAC 0.9 |
| Cable model | Copper; rho=0.0225 ohm mm2/m; resistance-only voltage drop; PE provisional |
| Thermal model | Base Iz values are illustrative inputs, all multiplied by 0.8. No installation table selection performed |
| Voltage-drop target | Internal educational target <5% end-to-end; not a verified compliance determination |
| Routes | Incoming 20 m, GF feeder 12 m, FF feeder 25 m; final circuits 20-45 m |
| Spare | Electrical headroom measured against highest phase demand; reserve >=20% physical ways separately |
| Exclusions | Fire alarm, smoke control, lift, PV, EV, generator, central emergency power, lightning, detailed ICT and HVAC design |

'''+sources)
write('docs/calculations.md',f'''# Calculation basis and worked examples

## Connected load and demand

All results are regenerated from `scripts/design_data.py`. CSVs are numeric snapshots, not live spreadsheets. Run the generator after changing inputs.

For each circuit: `P_connected = quantity x input power` or the documented estimated equipment allocation. `P_demand = P_connected x demand factor`. `S_demand = P_demand / PF`.

For 1-phase circuits: `I = P / (230 x PF)`. For 3-phase circuits: `P = sqrt(3) x V_LL x I x PF`, so `I = P / (sqrt(3) x 400 x PF)`.

Lighting circuit power includes its normal luminaires plus the normal charging/maintained input of its emergency fittings. Emergency loads are not added elsewhere.

{summary_table}
Building: `P_connected = {GF['w']} + {FF['w']} = {S['w']} W`. `P_demand = {GF['demand_w']:.0f} + {FF['demand_w']:.0f} = {S['demand_w']:.0f} W`.

Conservative apparent demand is the arithmetic sum of circuit VA, `{S['demand_va']:.2f} VA`. Effective calculation PF is `P_demand / sum(S) = {S['pf']:.4f}`. This is an arithmetic sizing proxy, not a phasor sum or measured aggregate PF.

`I_equivalent = {S['demand_w']:.0f} / (sqrt(3) x 400 x {S['pf']:.6f}) = {S['current']:.2f} A`. Select against actual phase totals as well: the highest diversified phase is `{S['max_current']:.2f} A`.

Nominal 400/230 V values cause a small difference between the balanced-equivalent calculation and the mean of phase currents. They are not silently forced to reconcile by changing voltage.

## Phase balance and headroom

Single-phase loads are assigned by descending connected current to the lightest phase. FF B/C labels are then exchanged to improve combined MSB demand balance. Three-phase loads contribute the same current to each phase.

{md(['Board','Connected A/B/C (A)','Demand A/B/C (A)','Demand headroom (A)','Demand headroom (%)'],[[f,' / '.join(f'{s['phase'][p]:.2f}' for p in 'ABC'),' / '.join(f'{s['md_phase'][p]:.2f}' for p in 'ABC'),f'{s['rating']-s['max_current']:.2f}',f'{100*(s['rating']-s['max_current'])/s['rating']:.1f}'] for f,s in [('DB-GF',GF),('DB-FF',FF),('MSB',S)]])}
Headroom is `(protective rating - highest phase demand)`, not unused circuit count. It does not establish distributor capacity. At full connected load, the highest MSB phase is `{max(S['phase'].values()):.2f} A`.

## Lighting lumen method

`E_average = total initial lumens x UF x MF / room area`.

GF open office: `24 x 4500 x 0.65 x 0.80 / 96 = 585 lx`. FF open office: `33 x 4500 x 0.65 x 0.80 / 132 = 585 lx`. Assumed task target is 400 lx, allowing later optimisation. Corridor: `10 x 2800 x 0.50 x 0.80 / 60 = 186.7 lx`.

See `lighting-lumen-method.csv` for every space. Lumen method estimates averages only; it does not demonstrate uniformity, glare, emergency illuminance, colour rendering or code compliance. Obtain photometric IES/LDT data and a room model for detailed verification.

## Conceptual cable sizing

Check `Ib <= In <= Iz_derated`, where `Iz_derated = assumed base Iz x 0.80`. The assumed base values (18 A for 1.5 mm2, 25 A for 2.5 mm2, 34 A for 4 mm2, 125 A for 25 mm2 and 220 A for 70 mm2) are deliberately illustrative placeholders. They are NOT certified cable ratings or AS/NZS 3008 table values. Real ratings depend on construction, insulation, installation, temperature, grouping and terminal limits.

Resistance estimate: `R_one_way = rho x L / A`, with `rho = 0.0225 ohm mm2/m`.

- 1-phase: `delta V = 2 x rho x L x I / A`.
- 3-phase: `delta V = sqrt(3) x rho x L x I / A`.
- `drop percent = 100 x delta V / nominal voltage`.

The resistance-only approximation omits reactance and uses full current rather than multiplying by cos(phi). It is a screening estimate, not a complete AC voltage-drop calculation. Upstream segments use maximum diversified phase current; final circuits use connected current. Add percentage drops along incoming + floor feeder + final circuit to screen against the internal 5% target.

{cabletable}
Worst screened complete path: `{max(cables,key=lambda c:c['total_pct'])['id']}`, `{max(c['total_pct'] for c in cables):.2f}%`.

The UPS feed represents server supply. No mains cable rating is inferred for the UPS output; vendor output distribution must be designed separately. PE areas, earth-fault loop impedance, disconnection time, adiabatic withstand, neutral harmonics and protective coordination remain unverified.
''')
report=f'''# Northbank Office - Conceptual Electrical Design

Revision A - {DATE}

## 1. Project Overview
An educational design package for a fictional two-storey Australian commercial office, covering 840 m2 gross. Ten editable LibreCAD-compatible DXF sheets are coordinated with circuit registers, calculations and this report.

This project is an educational electrical engineering portfolio exercise and is not intended for construction, certification, or regulatory approval.

## 2. Design Objectives
Demonstrate electrical CAD drafting, circuit planning, transparent load assumptions, phase balancing, distribution design and technical documentation. The primary quality criterion is consistency between plans, schedules, calculations and the single-line diagram.

## 3. Building Description
Each 30 x 14 m floor has a 2 m central corridor and stairs at opposite ends. All northern rooms have direct corridor doors. GF contains reception/waiting, open office, two meeting rooms, kitchen, male/female/accessible toilets, communications, electrical and storage rooms. FF contains open office, two managers' offices, conference and meeting rooms, kitchen, toilets including accessible WC, print area, storage and both stairs. The main entrance is at GF reception. Stair doors at ground level discharge outside. Door swings and stairs are diagrammatic; no architectural certification is implied.

## 4. Design Assumptions
See `design-assumptions.md` for the authoritative assumptions register. Supply is nominal 400/230 V at 50 Hz. Assumed floor-to-floor height is 3.6 m and ceiling height is 2.8 m. Equipment ratings and cable lengths are estimates. A complete architecture/access/fire review remains necessary, including inter-floor accessible access.

## 5. Electrical Supply
An assumed utility LV service enters the GF electrical room. The conceptual sequence is distributor service/metering, 200 A main isolator, 160 A main MCCB and 200 A MSB bus. Service arrangements, prospective short-circuit current, metering, neutral switching and approved supply capacity remain to be confirmed.

The MEN/TN-C-S concept places the main N-PE connection at the MSB, subject to distributor confirmation. N and PE remain separate downstream. Bonding, electrode arrangement and PE sizes require detailed design.

## 6. Distribution Philosophy
MSB feeds DB-GF and DB-FF independently through two 80 A feeders. DBs have assumed 125 A busbars and 100 A incoming isolators. A floor-board cascade was rejected because an independent radial arrangement avoids routing FF demand through DB-GF and improves isolation clarity. Four modest packaged HVAC loads remain on dedicated floor-board circuits; a separate mechanical board is unnecessary at this concept scale. Self-contained emergency devices avoid a central essential-services board. Fire/life-safety systems beyond lighting are excluded, not assumed unnecessary.

## 7. Lighting Design
Each floor uses eight lighting circuits. LP panels are assumed 36 W/4500 lm; LB battens 24 W/2800 lm. Open office lighting is split west/east, with separate circuits for meeting/office areas, kitchen/toilets, service rooms, corridor and stairs. Local switching and representative dashed control lines are shown. Stair control requires two-way switching or occupancy control with safe occupancy coverage.

The room-by-room lumen calculation uses assumed UF 0.50-0.65 and MF 0.80. Open office averages screen at 585 lx against a 400 lx assumed target. Fixture spacing is preliminary. Dimming and sensor zoning offer a later energy optimisation exercise. No product photometry, glare analysis or emergency lux calculation has been completed.

## 8. Power Distribution
Six general-power circuits per floor serve workstation banks, meeting/manager areas, reception/print/cleaning and kitchen small power. Each outlet symbol denotes a double 10 A socket. Circuit load is estimated appliance utilisation, not 20 A per double outlet. General circuits use proposed 20 A RCBOs and 4 mm2 Cu conductors to improve the 45 m voltage-drop estimate. These are provisional selections.

## 9. Dedicated Equipment
Each floor has dedicated fridge (0.25 kW), dishwasher (2 kW), microwave (1.5 kW), hot water (2.4 kW), copier (1.5 kW) and two three-phase HVAC units (6 kW electrical input each). GF adds a 2.2 kW UPS input and 0.4 kW non-UPS communications load. SERVER-01 (1.8 kW) and protected ICT (0.2 kW) sit downstream of UPS-01; their load is included in the input allowance and never counted twice. Vendor-specific local isolation, connection method, inrush and RCD compatibility need verification.

## 10. Emergency Lighting
E-301 covers escape corridors, both stairs, open office areas, the FF conference area and GF reception exit. Emergency luminaires are non-maintained; exit signs are maintained. Input allowance is 3 W each and assumed battery duration is 90 minutes. Unswitched taps from relevant local lighting circuits allow response to local normal supply failure. A DB test facility is proposed. Travel arrows and sign directions are conceptual. Confirm product spacing tables, viewing distance, mounting, egress, battery duty and AS/NZS 2293.1/NCC applicability.

## 11. Load Analysis
{summary_table}
Connected lighting includes normal emergency charging loads. General power represents allocated appliance estimates. HVAC values are electrical inputs, not cooling capacities. Circuit-level source values are in `schedules/load-schedule.csv`.

## 12. Maximum Demand
Demand factors are explicit engineering assumptions, not a claimed standards-based maximum-demand assessment: lighting 100%, general power 60%, fridge/dishwasher/microwave 80%, copier 60%, hot water/UPS/comms 100%, HVAC 90%. This gives {S['demand_w']/1000:.3f} kW and conservative apparent demand {S['demand_va']/1000:.3f} kVA. The balanced equivalent is {S['current']:.2f} A, while the highest calculated phase is {S['max_current']:.2f} A. The latter controls headroom checks. Demand assumptions require client/site validation.

## 13. Cable Sizing
{cabletable}
Use these as worked examples only. `calculations.md` explains thermal and voltage-drop formulae. All proposed circuits satisfy the illustrative Ib/In/Iz screen, but the Iz values are assumed and do not validate installation capacity. The worst accumulated resistance-only voltage drop is {max(c['total_pct'] for c in cables):.2f}% against an internal 5% target. Final design requires AS/NZS 3008 installation selection, derating, earth-loop and fault withstand verification.

## 14. Protection Philosophy
Separate floor feeder MCCBs and individual final-circuit RCBOs limit fault impact. A 30 mA Type A concept is used for single-phase final circuits. Three-phase HVAC requires manufacturer-specific protection/RCD assessment; no blanket Type A claim is made for inverter equipment. Breaker curves, interrupting capacity, backup protection and discrimination have not been selected without fault data. Neutral harmonic loading and surge protection requirements need review.

## 15. Distribution Board Schedules
E-501 is the drawing summary; the two DB CSVs hold complete descriptions, phases, input powers, currents, breaker ratings/types, cable construction, destinations, lengths and notes. Single-phase circuits are balanced on connected current; FF phase labels are rotated to improve combined MSB demand balance. Reserve at least 20% physical spare ways after counting actual module widths, separately from electrical headroom.

## 16. Single-Line Diagram
E-401 records the main supply and radial floor feeders, protective devices, bus ratings, major circuit groups, cable IDs and earthing concept. E-601 adds horizontal grouped routing and vertical riser R1. Feeder IDs C-M, C-GF and C-FF match cable schedules. No individual conductor routing or cable tray fill calculation is claimed.

## 17. Design Limitations
No site survey, distributor approval, formal compliance determination, fault study, discrimination study, certified cable selection, photometric model, emergency illuminance calculation or detailed architecture is included. Fire systems, smoke control, lift/access solution, detailed mechanical and communications design, PV/EV and generator supplies remain outside scope. All final design must be checked by suitably qualified practitioners against the current applicable standards and jurisdictional rules.

## 18. Skills Demonstrated
Layered electrical drafting; reusable CAD blocks; architectural coordination; circuit/equipment tagging; power and lighting design concepts; transparent load and demand analysis; phase allocation; resistance-based voltage-drop calculations; distribution schedules; single-line and riser diagrams; revision control and automated cross-file checks.

'''+sources
write('docs/engineering-report.md',report)
write('README.md',f'''# Northbank Office - Electrical Design Portfolio

A conceptual electrical design for a fictional Australian two-storey commercial office. Each floor is 30 x 14 m (420 m2), giving 840 m2 gross floor area.

**This project is an educational electrical engineering portfolio exercise and is not intended for construction, certification, or regulatory approval.**

## Start here

- [Engineering report](docs/engineering-report.md)
- [Design assumptions](docs/design-assumptions.md)
- [Calculation methods and worked examples](docs/calculations.md)
- [Validation record](docs/validation.md)

## Design scope

Normal and emergency lighting, exit signs, general and dedicated power, radial floor distribution, phase balancing, cable-route concepts, main SLD, schedules and explanatory calculations. The supply is 400/230 V three-phase, 50 Hz. MSB separately feeds DB-GF and DB-FF.

Connected load is {S['w']/1000:.3f} kW. Assumed maximum demand is {S['demand_w']/1000:.3f} kW, with highest diversified phase current {S['max_current']:.2f} A. See the report for the assumptions and limits of these figures.

## Software and file format

LibreCAD is the target CAD editor. Drawings use editable ASCII DXF R12 entities: LINE, CIRCLE, TEXT and INSERT/BLOCK. Geometry is authored by the included Python standard-library generator, avoiding proprietary CAD features and external dependencies. A JavaScript Artifact Tool exporter writes the requested numeric CSV schedules. SVG/PNG renders are provided for review.

The DXFs use **A2 sheet coordinates in model space**. Floor plans are plotted at 1:75, or 1:125 where marked. To convert a measured plan distance to real millimetres, multiply by the stated denominator. Text, symbols and title blocks are in plotted millimetres. This choice prioritises portable LibreCAD sheet editing and printing; it is not a full-size architectural BIM model.

## Drawings

'''+md(['Sheet','Drawing','DXF'],[[n,t,f'[Open](drawings/{stem}.dxf)'] for n,t,stem in __import__('generate_drawings').INDEX])+'''
Open a DXF in LibreCAD using File > Open, then View > Auto Zoom if needed. Use the layer list to isolate systems and the block list to reuse symbols. For printing, set A2 landscape, 1:1 paper scale and check the border fit in print preview. Do not apply an additional 1:75 print reduction.

## Engineering calculations and schedules

`schedules/` contains DB, equipment, cable, load, fixture, outlet and emergency registers. `calculations/` contains load totals, phase allocations, cable screening and room lumen-method results. CSVs are static numeric snapshots; formulae and source assumptions are documented and the Python model recalculates them.

## Screenshots and previews

![Ground-floor lighting](previews/E-101-ground-lighting.png)

![Main single-line diagram](previews/E-401-single-line-diagram.png)

All drawing sheets also have SVG previews, which remain crisp at high zoom.

## Reproduce or edit

1. Edit `scripts/design_data.py` for rooms, loads, devices and allocations.
2. Run `python scripts/generate_drawings.py`.
3. Run `python scripts/generate_engineering.py`.
4. In an environment with `@oai/artifact-tool`, run `node scripts/export_schedules.mjs`.
5. Run `python scripts/validate_project.py` for file/data consistency.
6. Inspect changed drawings in LibreCAD. Regenerate PNG previews from the SVGs with an SVG renderer if desired.

For environments without Artifact Tool, `python scripts/export_csv_fallback.py` reproduces the same requested CSV snapshots from the generated table data using the standard library.

Direct LibreCAD edits remain editable, but a generator rerun replaces the generated DXFs. Preserve a separate working revision before regenerating. Git may be used to track source and drawing revisions; this package is not automatically published.

## Skills demonstrated

Electrical CAD drafting, circuit allocation, lighting calculations, demand estimation, phase balancing, conceptual cable sizing, panel schedules, SLDs, cable routing and clear engineering documentation.

## Limitations

No compliance certification or construction suitability is claimed. Cable ampacities are illustrative inputs, equipment ratings are assumed, and photometric/fault/earthing/coordination studies remain incomplete. Architecture, fire/egress and accessible inter-floor access also require specialist review. See the report for the complete scope boundary.
''')
print('Engineering data and report generated:',len(tables),'CSV tables; max path drop',round(max(c['total_pct'] for c in cables),3))
