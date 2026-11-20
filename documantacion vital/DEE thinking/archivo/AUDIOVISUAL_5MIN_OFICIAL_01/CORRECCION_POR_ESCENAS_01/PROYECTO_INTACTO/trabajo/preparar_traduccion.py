"""Faithful English subtitle translation; Spanish remains the DOC01 source.
Translation is editorial, never an input to a DEE life.
"""
from pathlib import Path
import json,re
HERE=Path(__file__).resolve().parent
EN=[
[
'DEE Cognitive is an experimental system oriented towards intelligence.',
'It operates in a three-dimensional computational universe.',
'It has already demonstrated learning, memory, composition and communication in specific trials.',
'It is more than an idea.',
'It aims to retain experience and use it in new situations.',
'Some capabilities already work together.',
'Let us see how.'
],[
'Each cell is a location.',
'Its state contains information.',
'The engine rules determine how it changes when interacting.',
'An input encounters an existing organisation.',
'Its interactions produce a result, read at a defined location.',
'Here, physical means states and interactions in the model.',
'We are not showing particles from the outside world.'
],[
'An organisation can continue from its own history.',
'New inputs encounter its previous state, without starting from zero.',
'It can be saved and reopened with the necessary context.',
'Persistence means using what is retained and receiving new experiences, not learning without end.'
],[
'In memory trials, an experience changes relations within the world.',
'A later query can use that change.',
'Different histories are compared using the same query to isolate the effect of learning.',
'Association repertoires also exist, although retaining a state does not always guarantee access.'
],[
'In an integrated trial, a previously learned association was revised.',
'New inputs changed its response without changing the rules of the universe.',
'The other associations in the tested panel remained available.',
'This is selective revision in that trial, not a guarantee that all knowledge will be preserved.'
],[
'In composition, two contributions formed a common product.',
'That product was used in another interaction within the same world.',
'The case combines a history of order and contact.',
'Removing one contribution changes the consequence.',
'In this way, earlier relations produce results that can be reused.'
],[
'In communication, information acquired by one participant reached another and affected the receiver\'s later response.',
'Controls with interrupted messages or different content identify its effect.',
'This demonstrates transmitting and using information between defined participants, without claiming human conversation.'
],[
'Another trial connects anticipation and querying.',
'An earlier signal is compared with current information.',
'The discrepancy leads to a question within the world.',
'The question accesses acquired information that later contributes to a use.',
'The investigator prepares the opportunities and timing.'
],[
'In adaptation, the consequence of an action changed a reference.',
'That history influenced later actions when faced with the same opportunity.',
'Without the return, behaviour was different.',
'In another trial, an output acted on an external service, and its effect returned as experience.'
],[
'Learned regulation also appears in another experimental profile.',
'Different experiences changed the direction of a pulse that acted on an interference, changing a functional consequence.',
'This is local regulation: the geometry and opportunities remain prepared.',
'It does not demonstrate an autonomous decision about when to regulate.'
],[
'In functional language, a signal becomes associated with a use through experience.',
'Later, the signal can recover a related response.',
'The program encodes words as inputs.',
'The achievement is to acquire and use specific relations, not to hold a free conversation.'
],[
'In transfer, prior experience changed the first action in another context, before receiving a new consequence there.',
'With the opposite rule, it could also be detrimental.',
'History influences behaviour without guaranteeing correct responses.',
'Other trials integrated multiple contributions, with limits to access and continuity.'
],[
'These results come from identified trials.',
'Cognitive already allows associations, memory and comparison to be used in one instance with its own continuity.',
'Universe provides the dynamics; Thinking, the execution; and Cognitive, access and continuity.',
'Integration exists, but does not include all the experiments.'
],[
'DEE\'s interest lies in bringing capabilities together within its own computational dynamics: retaining experience, revising it, combining it and using information.',
'This basis allows adaptive agents and new forms of memory and processing to be explored.',
'Specific applications and advantages must be evaluated through testing.',
'DEE Cognitive: demonstrated capabilities, an intelligent system in development.',
'The invitation is to investigate, reproduce and develop.'
]]

script=json.loads((HERE/'audio/guion.json').read_text('utf8'))
out=[]
for block,eng in zip(script['blocks'],EN):
 es=[s.strip() for s in re.findall(r'[^.!?]+[.!?]',block['literal_ES'])]
 assert len(es)==len(eng),(block['id'],len(es),len(eng))
 out.append({'block':block['block'],'start_s':block['start_s'],'end_s':block['end_s'],
 'literal_ES':block['literal_ES'],'sentences':[{'ES':a,'EN':b} for a,b in zip(es,eng)]})
(HERE/'TRADUCCION_EN.json').write_text(json.dumps({'schema':'DEE.5min.literal_translation.v1','Spanish_source':script['source'],'blocks':out,'scope':'faithful subtitles, no claimed generalisation beyond Spanish'},ensure_ascii=False,indent=2),'utf8')
print('Translation:',len(out),'blocks,',sum(len(x['sentences']) for x in out),'sentences')
