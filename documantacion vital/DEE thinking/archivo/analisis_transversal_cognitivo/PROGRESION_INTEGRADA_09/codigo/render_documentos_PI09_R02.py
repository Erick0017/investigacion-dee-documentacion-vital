"""Second actual render attempt, edition1.38; preserves literal edition1.37 tool."""
from pathlib import Path
import hashlib

original = Path(__file__).with_name('render_documentos_PI09_R01.py')
data = original.read_bytes()
assert hashlib.sha256(data).hexdigest() == '022a3cf1dc18dcc389fe59c663168019acaf964fb7bb0f1b9e4eddce4b8da435'
source = data.decode('utf-8-sig')
assert '1_37' in source
updated = source.replace('1_37', '1_38')
assert '1_37' not in updated
exec(compile(updated, str(Path(__file__).resolve()), 'exec'),
     {'__name__': '__main__', '__file__': str(Path(__file__).resolve())})
