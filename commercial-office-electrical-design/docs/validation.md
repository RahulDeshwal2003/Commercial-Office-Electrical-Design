# Validation record - Revision A

## Numerical and structural checks

`scripts/validate_project.py` checks the saved DXF and CSV files against the design model. The latest run passed 638 assertions covering circuit uniqueness, board allocation, room areas, load totals, fixture and emergency load reconciliation, device references, phase assignments, proposed breaker current, illustrative cable-capacity inequalities, voltage-drop screening and room lumen arithmetic.

The ten indexed DXFs were checked for balanced group/value records, EOF markers, valid block references, drawing identifiers, concept status and absence of proprietary proxy/3D entities. These are format and consistency checks, not an independent electrical design certification.

| Item | Result |
| --- | --- |
| Final circuits | 44 |
| Normal luminaires | 171 |
| Emergency luminaires and exit signs | 40 |
| Double general outlets | 62 |
| Dedicated equipment connections | 16 |
| Connected input | 75.104 kW |
| Assumed maximum demand | 58.964 kW |
| Highest diversified phase current | 92.019 A |
| Worst resistance-only accumulated drop | 3.731% |

## Visual review

All ten sheet previews were rendered and reviewed for layout, title blocks, readable labels and diagram completeness. Board symbols were moved away from nearby lighting symbols and the grouped power routes were connected to the board locations. Previews are companion vector renders from the same drawing geometry; they are not LibreCAD screen captures.

## LibreCAD checks

The ground-floor lighting drawing was opened in LibreCAD and fitted to its full extent. Its architectural and electrical layers, lighting symbols and labels loaded. The cover drawing was opened, fitted and saved from LibreCAD successfully; the saved file passed the structural validation again. The single-line drawing was also opened for inspection. Native checks are representative, not a claim that every sheet was individually opened and printed.

LibreCAD may simplify small text at distant zoom. Zoom in to inspect labels. Set A2 landscape and a 1:1 paper scale for printing the pre-scaled sheets. A physical print/plot and product-specific photometric verification were not performed.

## Remaining engineering verification

All equipment powers, diversity factors, cable ampacities, protection ratings, route lengths and lighting factors are concept assumptions. Fault levels, protective coordination, earthing, neutral harmonics, actual installation derating, emergency photometry, fire/egress and accessible inter-floor access remain unresolved. No standards-compliance or construction-suitability conclusion follows from the automated checks.
