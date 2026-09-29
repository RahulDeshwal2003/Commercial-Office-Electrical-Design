# Calculation basis and worked examples

## Connected load and demand

All results are regenerated from `scripts/design_data.py`. CSVs are numeric snapshots, not live spreadsheets. Run the generator after changing inputs.

For each circuit: `P_connected = quantity x input power` or the documented estimated equipment allocation. `P_demand = P_connected x demand factor`. `S_demand = P_demand / PF`.

For 1-phase circuits: `I = P / (230 x PF)`. For 3-phase circuits: `P = sqrt(3) x V_LL x I x PF`, so `I = P / (sqrt(3) x 400 x PF)`.

Lighting circuit power includes its normal luminaires plus the normal charging/maintained input of its emergency fittings. Emergency loads are not added elsewhere.

| Board | Connected kW | Demand kW | Demand kVA | Equivalent A | Highest phase A | Breaker A |
| --- | --- | --- | --- | --- | --- | --- |
| DB-GF | 38.789 | 30.719 | 32.769 | 47.30 | 49.74 | 80 |
| DB-FF | 36.315 | 28.245 | 30.164 | 43.54 | 46.45 | 80 |
| MSB | 75.104 | 58.964 | 62.933 | 90.84 | 92.02 | 160 |

Building: `P_connected = 38789 + 36315 = 75104 W`. `P_demand = 30719 + 28245 = 58964 W`.

Conservative apparent demand is the arithmetic sum of circuit VA, `62932.87 VA`. Effective calculation PF is `P_demand / sum(S) = 0.9369`. This is an arithmetic sizing proxy, not a phasor sum or measured aggregate PF.

`I_equivalent = 58964 / (sqrt(3) x 400 x 0.936935) = 90.84 A`. Select against actual phase totals as well: the highest diversified phase is `92.02 A`.

Nominal 400/230 V values cause a small difference between the balanced-equivalent calculation and the mean of phase currents. They are not silently forced to reconcile by changing voltage.

## Phase balance and headroom

Single-phase loads are assigned by descending connected current to the lightest phase. FF B/C labels are then exchanged to improve combined MSB demand balance. Three-phase loads contribute the same current to each phase.

| Board | Connected A/B/C (A) | Demand A/B/C (A) | Demand headroom (A) | Demand headroom (%) |
| --- | --- | --- | --- | --- |
| DB-GF | 59.86 / 60.12 / 59.41 | 49.15 / 43.37 / 49.74 | 30.26 | 37.8 |
| DB-FF | 56.14 / 56.30 / 55.63 | 42.87 / 46.45 / 41.62 | 33.55 | 41.9 |
| MSB | 116.00 / 116.43 / 115.04 | 92.02 / 89.82 / 91.36 | 67.98 | 42.5 |

Headroom is `(protective rating - highest phase demand)`, not unused circuit count. It does not establish distributor capacity. At full connected load, the highest MSB phase is `116.43 A`.

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

| Circuit | Ib A | In A | Cu mm2 | Length m | Assumed derated Iz A | Drop % | Total path % |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C-M | 92.02 | 160 | 70 | 20 | 176.0 | 0.26 | 0.26 |
| C-GF | 49.74 | 80 | 25 | 12 | 100.0 | 0.23 | 0.49 |
| C-FF | 46.45 | 80 | 25 | 25 | 100.0 | 0.45 | 0.71 |
| GF-L01 | 1.99 | 10 | 1.5 | 35 | 14.4 | 0.91 | 1.40 |
| GF-P01 | 10.98 | 20 | 4 | 45 | 27.200000000000003 | 2.42 | 2.91 |
| GF-UPS01 | 10.07 | 16 | 2.5 | 20 | 20.0 | 1.58 | 2.06 |
| GF-AC01 | 9.62 | 16 | 4 | 45 | 27.200000000000003 | 1.05 | 1.54 |

Worst screened complete path: `FF-P06`, `3.73%`.

The UPS feed represents server supply. No mains cable rating is inferred for the UPS output; vendor output distribution must be designed separately. PE areas, earth-fault loop impedance, disconnection time, adiabatic withstand, neutral harmonics and protective coordination remain unverified.
