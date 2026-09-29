import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Workbook } from '@oai/artifact-tool';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const tables=JSON.parse(await fs.readFile(path.join(root,'scripts/schedule-data.json'),'utf8'));
const quote=v=>{const s=v==null?'':String(v);return /[",\r\n]/.test(s)?'"'+s.replaceAll('"','""')+'"':s;};
for(const [name,rows] of Object.entries(tables)){
  const wb=Workbook.create();const sh=wb.worksheets.add('Schedule');
  sh.getRangeByIndexes(0,0,rows.length,rows[0].length).values=rows;
  wb.recalculate();
  const values=sh.getRangeByIndexes(0,0,rows.length,rows[0].length).values;
  if(values.length!==rows.length)throw new Error('Export row count mismatch: '+name);
  await fs.writeFile(path.join(root,name),values.map(r=>r.map(quote).join(',')).join('\r\n')+'\r\n');
  console.log(name+': '+(values.length-1)+' records');
}
