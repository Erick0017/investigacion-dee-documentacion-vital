import { Workbook } from '@oai/artifact-tool';
const wb=Workbook.create();
console.log(wb.help('workbook.inspect',{include:'index,examples,notes',maxChars:3500}));
