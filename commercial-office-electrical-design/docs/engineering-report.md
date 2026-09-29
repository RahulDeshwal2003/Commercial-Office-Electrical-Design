# Northbank Office - Conceptual Electrical Design

Revision A - 2026-09-29

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
| Board | Connected kW | Demand kW | Demand kVA | Equivalent A | Highest phase A | Breaker A |
| --- | --- | --- | --- | --- | --- | --- |
| DB-GF | 38.789 | 30.719 | 32.769 | 47.30 | 49.74 | 80 |
| DB-FF | 36.315 | 28.245 | 30.164 | 43.54 | 46.45 | 80 |
| MSB | 75.104 | 58.964 | 62.933 | 90.84 | 92.02 | 160 |

Connected lighting includes normal emergency charging loads. General power represents allocated appliance estimates. HVAC values are electrical inputs, not cooling capacities. Circuit-level source values are in `schedules/load-schedule.csv`.

## 12. Maximum Demand
Demand factors are explicit engineering assumptions, not a claimed standards-based maximum-demand assessment: lighting 100%, general power 60%, fridge/dishwasher/microwave 80%, copier 60%, hot water/UPS/comms 100%, HVAC 90%. This gives 58.964 kW and conservative apparent demand 62.933 kVA. The balanced equivalent is 90.84 A, while the highest calculated phase is 92.02 A. The latter controls headroom checks. Demand assumptions require client/site validation.

## 13. Cable Sizing
| Circuit | Ib A | In A | Cu mm2 | Length m | Assumed derated Iz A | Drop % | Total path % |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C-M | 92.02 | 160 | 70 | 20 | 176.0 | 0.26 | 0.26 |
| C-GF | 49.74 | 80 | 25 | 12 | 100.0 | 0.23 | 0.49 |
| C-FF | 46.45 | 80 | 25 | 25 | 100.0 | 0.45 | 0.71 |
| GF-L01 | 1.99 | 10 | 1.5 | 35 | 14.4 | 0.91 | 1.40 |
| GF-P01 | 10.98 | 20 | 4 | 45 | 27.200000000000003 | 2.42 | 2.91 |
| GF-UPS01 | 10.07 | 16 | 2.5 | 20 | 20.0 | 1.58 | 2.06 |
| GF-AC01 | 9.62 | 16 | 4 | 45 | 27.200000000000003 | 1.05 | 1.54 |

Use these as worked examples only. `calculations.md` explains thermal and voltage-drop formulae. All proposed circuits satisfy the illustrative Ib/In/Iz screen, but the Iz values are assumed and do not validate installation capacity. The worst accumulated resistance-only voltage drop is 3.73% against an internal 5% target. Final design requires AS/NZS 3008 installation selection, derating, earth-loop and fault withstand verification.

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

## Reference framework

- [NSW Fair Trading: electrical standards, rules and notes](https://www.fairtrading.nsw.gov.au/trades-and-businesses/construction-and-trade-essentials/electricians/standards-rules-and-notes) identifies the Wiring Rules as an installation safety reference.
- [ABCB: NCC 2022 Part E4](https://ncc.abcb.gov.au/editions/ncc-2022/adopted/volume-one/e-services-and-equipment/part-e4-visibility-emergency-exit-signs-and-warning-systems) describes emergency visibility, exit identification and the AS/NZS 2293.1 framework.

These public references were checked on 29 September 2026 for context, not to certify current project applicability. NCC 2022 is a reference edition, not an assertion of the edition adopted in a particular jurisdiction on the design date. Obtain current adopted NCC provisions, amendments, distributor service rules and licensed copies of applicable AS/NZS 3000, 3008.1.1, 2293.1, 1680 and 61439 requirements before detailed design. No standard tables or mandatory lux values have been reproduced or claimed as verified.
