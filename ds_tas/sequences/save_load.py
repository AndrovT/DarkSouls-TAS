
import json
from .basics import (
    sequence,
    seq_factory,
)
from ds_tas.engine.tas_engine import InputState


@seq_factory
def record(seq, file):
    @sequence('unk')
    def fn(hook):
        with open(file, 'w') as f:
            for inp in seq(hook):
                f.write(json.dumps(inp.key_list)+'\n')
                yield inp
    return fn


@seq_factory
def replay(file):
    @sequence('unk')
    def fn(hook):
        with open(file) as f:
            for line in f:
                yield InputState.from_list(json.loads(line))
    return fn
