# Design assumptions - Revision A

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

## Reference framework

- [NSW Fair Trading: electrical standards, rules and notes](https://www.fairtrading.nsw.gov.au/trades-and-businesses/construction-and-trade-essentials/electricians/standards-rules-and-notes) identifies the Wiring Rules as an installation safety reference.
- [ABCB: NCC 2022 Part E4](https://ncc.abcb.gov.au/editions/ncc-2022/adopted/volume-one/e-services-and-equipment/part-e4-visibility-emergency-exit-signs-and-warning-systems) describes emergency visibility, exit identification and the AS/NZS 2293.1 framework.

These public references were checked on 29 September 2026 for context, not to certify current project applicability. NCC 2022 is a reference edition, not an assertion of the edition adopted in a particular jurisdiction on the design date. Obtain current adopted NCC provisions, amendments, distributor service rules and licensed copies of applicable AS/NZS 3000, 3008.1.1, 2293.1, 1680 and 61439 requirements before detailed design. No standard tables or mandatory lux values have been reproduced or claimed as verified.
