import fs from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";
import { Workbook } from "@oai/artifact-tool";

// Only a reviewed data matrix is authored. This program never loads the motor.
const [input, output] = process.argv.slice(2);
if (!input || !output) throw new Error("Reviewed JSON and fresh output directory required");
const data = JSON.parse(await fs.readFile(input, "utf8"));
const tables = Array.isArray(data.tables) ? data.tables : Object.entries(data.tables).map(([name,t]) => ({
  filename:name+".csv", headers:t.headers,
  rows:t.rows.map(row=>t.headers.map(key=>row[key]))
}));
if (data.status !== "FINAL_TABLE_DATA_APPROVED" || tables.length !== 3)
  throw new Error("Three approved, non-provisional tables required");
await fs.mkdir(output, {recursive: true});
const sha = bytes => crypto.createHash("sha256").update(bytes).digest("hex");
const report = {schema:"APD02.tables.artifact_tool.v1", input, input_sha256:sha(await fs.readFile(input)), tables:[], native_ticks:0};
function col(n) { let s=""; for(n++;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s; return s; }
function csv(v) {
  const s=v===null ? "" : String(v);
  if (/^[=+@]/.test(s)) throw new Error("Unexpected formula-like authored cell");
  return /[\r\n",]/.test(s) ? '"'+s.replace(/"/g,'""')+'"' : s;
}
for (const t of tables) {
  if (!/^[A-Z0-9_]+\.csv$/.test(t.filename)) throw new Error("Bad table member");
  const matrix = [t.headers,...t.rows];
  if (matrix.length < 2 || matrix.some(r=>r.length!==t.headers.length))
    throw new Error("Nonrectangular/empty table");
  for (const r of matrix) for(const v of r)
    if (!["string","number","boolean"].includes(typeof v) && v!==null) throw new Error("Scalar cell required");
  for (const r of matrix) for(const v of r)
    if(typeof v==="number" && (!Number.isFinite(v) || (Number.isInteger(v)&&!Number.isSafeInteger(v))))
      throw new Error("Unsafe numeric value; RAW and hashes must remain exact text");
  const wb=Workbook.create(), sheet=wb.worksheets.add("Datos");
  const full=sheet.getRange("A1:"+col(t.headers.length-1)+matrix.length);
  full.values=matrix;
  full.format.font.name="Aptos"; full.format.font.size=11;
  full.format.wrapText=true; full.format.verticalAlignment="top";
  full.format.columnWidth=30;
  const header=sheet.getRange("A1:"+col(t.headers.length-1)+"1");
  header.format.fill="#16324F"; header.format.font.color="#FFFFFF"; header.format.font.bold=true;
  sheet.freezePanes.freezeRows(1); sheet.showGridLines=false;
  full.format.autofitRows();
  wb.recalculate();
  const actual=full.values;
  if(JSON.stringify(actual)!==JSON.stringify(matrix)) throw new Error("Artifact matrix changed source values");
  const inspect=await wb.inspect({kind:"table",range:"Datos!A1:"+col(t.headers.length-1)+Math.min(matrix.length,8),
    include:"values,formulas",tableMaxRows:8,tableMaxCols:t.headers.length,maxChars:6000});
  const errors=await wb.inspect({kind:"match",searchTerm:"#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#SPILL!|#CALC!",
    options:{useRegex:true,maxResults:50},summary:"No formulas are authored"});
  const content="\uFEFF"+actual.map(r=>r.map(csv).join(",")).join("\r\n")+"\r\n";
  const target=path.join(output,t.filename);
  await fs.writeFile(target,content,{encoding:"utf8",flag:"wx"});
  const preview=await wb.render({sheetName:"Datos",range:"A1:"+col(Math.min(t.headers.length-1,3))+Math.min(matrix.length,7),scale:1.4,format:"png"});
  const png=path.join(output,t.filename.replace(".csv","_QA.png"));
  await fs.writeFile(png,new Uint8Array(await preview.arrayBuffer()),{flag:"wx"});
  report.tables.push({filename:t.filename,rows:t.rows.length,columns:t.headers.length,sha256:sha(await fs.readFile(target)),bytes:(await fs.stat(target)).size,
    exact_matrix_match:true,inspection:inspect.ndjson,error_scan:errors.ndjson,preview:png,render_scope:"First four columns and first seven rows; full CSV equality separately verified"});
}
await fs.writeFile(path.join(output,"VERIFICACION_TABLAS_ARTIFACT.json"),JSON.stringify(report,null,2),{flag:"wx"});
console.log(JSON.stringify({tables:report.tables.map(({filename,rows,columns,sha256,bytes,exact_matrix_match})=>({filename,rows,columns,sha256,bytes,exact_matrix_match})),native_ticks:0}));

