"""Portable re-generation option for users without Artifact Tool."""
from pathlib import Path
import csv,json
r=Path(__file__).resolve().parents[1]
for name,rows in json.loads((r/'scripts/schedule-data.json').read_text()).items():
    with (r/name).open('w',newline='',encoding='utf8') as f:csv.writer(f).writerows(rows)
