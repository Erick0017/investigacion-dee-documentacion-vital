"""Pure literal union; runtime dispatch still checks the exact current life.

No Native result, context datum, correct answer or operand chooses a policy.
Historical R02 material literals remain admissible only for canonical Native;
the Discovery world dispatcher rejects those in favour of its own D calendar.
"""
def validate_literal(row):
 if not isinstance(row,dict)or not isinstance(row.get('modo'),str):raise ValueError('Se requiere un literal PI09 explícito')
 if row['modo']in('eci01-pi09-preparar','eci01-pi09-episodio','eci01-pi09-estado'):
  from capacidades import pi09_dispatcher_R02 as original
  return original.validate_literal(row)
 from capacidades import pi09_dispatcher_D_R02 as current
 return current.validate_literal(row)
