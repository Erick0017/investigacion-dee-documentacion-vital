'use strict';
// N0 presentation proposal only. Not part of the frozen live application.
// Receipt counts describe admission; they never solve or correct a DEE answer.
function admissionLabel(requests) {
  const rows = Array.isArray(requests) ? requests : [];
  const statuses = rows.map(item => item.receipt?.status ?? 'sin_recibo');
  const applied = statuses.filter(value => value === 'applied').length;
  const rejected = statuses.filter(value => value.startsWith('rejected')).length;
  const complete = rows.length > 0 && applied === rows.length;
  return {complete, text: `${applied}/${rows.length} entradas aplicadas; ${rejected} rechazadas`,
    caution: complete ? '' : rows.length === 0 ? 'admisión no comprobada' : applied === 0 ? 'consulta no admitida' : 'consulta incompleta'};
}

function describePhysicalRow(row) {
  const parts = [], reader = row.reader || row.word?.reader;
  if (reader) {
    const admission = admissionLabel(row.requests || row.word?.requests);
    const signal = reader.ambiguous ? 'emisión ambigua' : reader.formed_native_command == null ? 'sin emisión formada' : 'señal ' + reader.formed_native_command;
    parts.push(`${admission.complete ? 'ENTE: emisión física registrada' : 'INSTRUMENTO: señal física observada'} · ${row.form || row.literal_form || 'forma'} → ${signal} (${admission.text})${admission.complete ? '' : '; ' + admission.caution + '; no uso actual demostrado'}`);
  }
  if (row.native_numeric?.numeric_reader) {
    const admission = admissionLabel(row.native_numeric.native_trial?.requests);
    const result = row.native_numeric.numeric_reader.numeric_result;
    parts.push(`${admission.complete ? 'ENTE: lectura numérica física' : 'INSTRUMENTO: lectura numérica observada'} ${result ?? 'no formada'} (${admission.text})${admission.complete ? '' : '; ' + admission.caution + '; no cálculo actual demostrado'}`);
  }
  if (row.committed_effect?.used_value !== undefined) {
    parts.push(`${row.selected_procedure === 'native' ? 'EFECTO: herramienta nativa preparada' : 'HERRAMIENTA preparada'} · valor comprometido ${row.committed_effect.used_value}; no certifica por sí solo corrección ni aprendizaje`);
  }
  if (row.physical_action !== undefined) {
    parts.push(`ENTE: salida ${row.physical_action ?? 'sin acción formada'}; ENTORNO: ${row.committed_effect?.reason || 'consecuencia registrada'}`);
  }
  return parts.length ? parts.join(' · ') : row.kind || '';
}

if (typeof module !== 'undefined') module.exports = {admissionLabel, describePhysicalRow};
