'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const proposal = path.resolve(__dirname, '../../../laboratorio/campanas/APD05_GENESIS_SIN_LLM/PROPUESTA_ROTULO_ADMISION_GUI_R01.js');
const vm = require('node:vm');
const application = path.resolve(__dirname, '../app.js');
const appBytes = fs.readFileSync(application, 'utf8');
const start = appBytes.indexOf('function admissionLabel('), end = appBytes.indexOf('function summarize(', start);
assert.ok(start >= 0 && end > start, 'R06 presentation functions must exist in the actual application');
const {admissionLabel, describePhysicalRow} = vm.runInNewContext(appBytes.slice(start, end) + '\n({admissionLabel, describePhysicalRow})', {});
const applied = {receipt: {status: 'applied'}};
const rejected = {receipt: {status: 'rejected_occupied'}};
const reader = {ambiguous: false, formed_native_command: -1};
const rows = [
  {name: 'all_rejected_resident_signal', row: {form: 'clasifica', reader, requests: Array(4).fill(rejected)}, expected: ['INSTRUMENTO', '0/4', 'consulta no admitida', 'no uso actual demostrado']},
  {name: 'partial_admission', row: {form: 'equilibra', reader, requests: [applied, ...Array(175).fill(rejected)]}, expected: ['INSTRUMENTO', '1/176', 'consulta incompleta', 'no uso actual demostrado']},
  {name: 'all_applied_finite_lexical_query', row: {form: 'luma', reader, requests: Array(7).fill(applied)}, expected: ['ENTE: emisión física registrada', '7/7']},
  {name: 'no_receipts_not_admission', row: {form: 'nara', reader}, expected: ['INSTRUMENTO', 'admisión no comprobada']},
  {name: 'numeric_rejected_not_computation', row: {native_numeric: {numeric_reader: {numeric_result: 27}, native_trial: {requests: [rejected, rejected]}}}, expected: ['INSTRUMENTO', '27', 'no cálculo actual demostrado']},
  {name: 'effect_is_distinct_from_lexical_emission', row: {literal_form: 'suma', word: {reader, requests: [applied]}, committed_effect: {used_value: 9}, selected_procedure: 'external'}, expected: ['ENTE: emisión física registrada', 'HERRAMIENTA preparada', 'valor comprometido 9', 'no certifica por sí solo corrección ni aprendizaje']}
];
const results = rows.map(test => {
  const text = describePhysicalRow(test.row);
  for (const expected of test.expected) assert.ok(text.includes(expected), `${test.name}: ${expected}`);
  return {name: test.name, text, expected_strings_present: true};
});
assert.equal(admissionLabel([]).complete, false);
assert.equal(admissionLabel([{}]).complete, false);
assert.equal(admissionLabel([applied]).complete, true);
console.log(JSON.stringify({scope: 'N0 actual R06 presentation functions; no Native import, HTTP actions or ticks', proposal, application, rows: results}, null, 2));
