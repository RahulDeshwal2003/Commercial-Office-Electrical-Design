"""Create a clean handoff archive, excluding caches and LibreCAD backup files."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
r=Path(__file__).resolve().parents[1]
target=r.parent/'commercial-office-electrical-design.zip'
with ZipFile(target,'w',ZIP_DEFLATED) as z:
    for p in sorted(r.rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts and 'node_modules' not in p.parts and not p.name.endswith(('~','.pyc')):
            z.write(p,str(Path(r.name)/p.relative_to(r)))
with ZipFile(target) as z:
    assert z.testzip() is None
    assert len([n for n in z.namelist() if '/drawings/' in n and n.endswith('.dxf')])==10
    print(f'Archive verified: {len(z.namelist())} files; {target.stat().st_size} bytes')
