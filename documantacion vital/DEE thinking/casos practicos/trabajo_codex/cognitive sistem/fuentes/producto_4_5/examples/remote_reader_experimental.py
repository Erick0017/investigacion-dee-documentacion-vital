"""Installed finite CPC6 reader: experience, new opaque form, remote reuse."""
import json
from dee_thinking.remote_reader import RemoteReaderSession

s=RemoteReaderSession.create()
s.experience_order('BA')
s.acquire_sources(1,-1)
s.late_use()
s.run_until(5)
s.consequence(1)
s.run_until(34)
s.teach_first_form()
s.query_first_form(tick=50)
s.learn_second_form()
s.query_first_form(tick=117)
s.run_until(162)
print(json.dumps({'profile':'EXPERIMENTAL_CPC6_FINITE_REMOTE_READER','readings':s.readings,
                  'receipts':s.receipts(),'scope':'Two scoped opaque associations and a fixed delayed reader, not a stable general language system.'},ensure_ascii=False))
