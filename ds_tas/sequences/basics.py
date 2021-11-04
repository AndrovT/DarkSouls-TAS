"""Provides core tools to build sequences.
"""
from itertools import chain, zip_longest, islice
from functools import wraps,  total_ordering
from abc import ABC, abstractmethod
from ds_tas.engine.tas_engine import InputState


__all__ = [
    'Chain',
    'Shortest',
    'Longest',
    'sequence',
    'seq_factory',
    'repeat',
    'wait',
    'none',
    'call',
]


@total_ordering
class Length:
    def __new__(cls, value):
        try:
            value = int(value)
        except ValueError:
            return super().__new__(cls)

        if value >= 0:
            return value
        raise ValueError(f'{value} is not valid length.')

    def __init__(self, value):
        if isinstance(value, str):
            if value.lower() == 'inf':
                self._value = 'inf'
            elif value.lower() == 'unk':
                self._value = 'unk'
            else:
                raise ValueError(f"'{value}' is not valid length.")
        else:
            raise ValueError(f"'{value}' is not valid length.")

    def __str__(self):
        return str(self._value)

    def __repr__(self):
        return f"Length('{self._value}')"

    def __eq__(self, other):
        if isinstance(other, (Length, int)):
            if self._value == 'unk':
                raise ValueError('Cannot compare unknown lengths.')
            elif isinstance(other, Length):
                if other._value == 'unk':
                    raise ValueError('Cannot compare unknown lengths.')
                return self._value == other._value
            elif isinstance(other, int):
                return False
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, (Length, int)):
            if self._value == 'unk':
                raise ValueError('Cannot compare unknown lengths.')
            elif isinstance(other, Length):
                if other._value == 'unk':
                    raise ValueError('Cannot compare unknown lengths.')
                return False
            elif isinstance(other, int):
                return False
        return NotImplemented

    def __add__(self, other):
        if isinstance(other, (Length, int)):
            if self._value == 'inf':
                return Length('inf')
            elif isinstance(other, Length):
                if other._value == 'inf':
                    return Length('inf')

            return Length('unk')
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, (Length, int)):
            if self._value == 'inf':
                return Length('inf')
            elif isinstance(other, Length):
                if other._value == 'inf':
                    return Length('inf')

            return Length('unk')
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, (Length, int)):
            if isinstance(other, Length):
                raise ValueError(f"Cannot subtract '{other}'")
            if self._value == 'inf':
                return Length('inf')

            return Length('unk')
        return NotImplemented

    def __rsub__(self, other):
        raise ValueError(f"Cannot subtract '{self}'")


class Sequence(ABC):
    def __init__(self, name=None):
        self.name = name
        self.len = Length('unk')

    @abstractmethod
    def __call__(self, hook):
        return NotImplemented

    def __repr__(self):
        return self.name or super().__repr__()

    def __len__(self):
        if isinstance(self.len, int):
            return self.len
        if self.len._value == 'unk':
            raise ValueError(f"'{self}' has unknown length.")
        if self.len._value == 'inf':
            raise ValueError(f"'{self}' has infinite length.")

    def __getitem__(self, key):
        key = self.normalize_key(key)
        return Slice(self, key.start, key.stop, key.step)

    def __or__(self, other):
        if isinstance(other, (Sequence, int)):
            return Longest(self, other)
        else:
            return NotImplemented

    def __ror__(self, other):
        if isinstance(other, (Sequence, int)):
            return Longest(other, self)
        else:
            return NotImplemented

    def __and__(self, other):
        if isinstance(other, (Sequence, int)):
            return Shortest(self, other)
        else:
            return NotImplemented

    def __rand__(self, other):
        if isinstance(other, (Sequence, int)):
            return Shortest(other, self)
        else:
            return NotImplemented

    def __add__(self, other):
        if isinstance(other, (Sequence, int)):
            return Chain(self, other)
        else:
            return NotImplemented

    def __radd__(self, other):
        if isinstance(other, (Sequence, int)):
            return Chain(other, self)
        else:
            return NotImplemented

    def __mul__(self, other):
        if isinstance(other, int):
            return Chain(*[self]*other)
        else:
            return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def normalize_key(self, key):
        if isinstance(key, int):
            start = key
            stop = key + 1
            step = 1
        elif isinstance(key, slice):
            start = key.start or 0
            stop = key.stop
            step = key.step if key.step is not None else 1
        else:
            raise ValueError("Key must be slice or int")

        if start < 0:
            if isinstance(self.len, int):
                start += self.len+1
            else:
                raise ValueError(
                    "Start argument for Slice can only be negative for known finite length sequences"
                )
        if stop is not None and stop < 0:
            if isinstance(self.len, int):
                stop += self.len+1
            else:
                raise ValueError(
                    "Stop argument for Slice can only be negative for known finite length sequences"
                )
        if step <= 0:
            raise ValueError(
                "Step argument for Slice must be positive"
            )

        return slice(start, stop, step)

# Sequence operation results


class Chain(Sequence):
    """Chains multiple sequences together. An integers i is interpreted as
    wait*i.
    """
    def __init__(self, *inputs):
        super().__init__(f'Chain{inputs!r}')
        self._chain = []
        for item in inputs:
            if isinstance(item, Chain):
                self._chain.extend(item._chain)
            elif isinstance(item, Sequence):
                self._chain.append(item)
            elif isinstance(item, int):
                self._chain.extend((wait*item)._chain)
            else:
                raise AttributeError
        self.len = sum([item.len for item in self._chain])

    def __call__(self, hook):
        return chain.from_iterable((item(hook) for item in self._chain))

    def __getitem__(self, key):
        key = self.normalize_key(key)

        new = []
        start = key.start
        stop = key.stop
        step = key.step

        for i in range(len(self._chain)):
            if not isinstance(self._chain[i].len, int):
                new.append(Slice(Chain(*self._chain[i:]), start, stop, step))
                break
            if start < self._chain[i].len:
                new.append(self._chain[i][start:stop:step])
            start = max(0, start-self._chain[i].len)
            if stop is not None:
                stop -= self._chain[i].len
            if stop is not None and stop <= 0:
                break
        return Chain(*new)



    '''@classmethod
    def from_iterable(cls, iterable):
        """Evaluates iterable lazily.
        """
        obj = cls()
        obj.name = f'Chain.from_iterable({iterable!r})'
        obj._chain = iterable
        return obj'''


class Shortest(Sequence):
    """Combination inputs.

    For each input field takes the right most defined value. Truncates
    sequences to the shortest input length. An integers i is interpreted as
    wait*i.
    """
    def __init__(self, *inputs):
        super().__init__(f'Shortest{inputs!r}')
        self._inputs = []
        for item in inputs:
            if isinstance(item, Shortest):
                self._inputs.extend(item._inputs)
            elif isinstance(item, Sequence):
                self._inputs.append(item)
            elif isinstance(item, int):
                self._inputs.append(wait*item)
            else:
                raise AttributeError

        try:
            self.len = min([item.len for item in self._inputs])
        except ValueError:
            self.len = Length('unk')

    def __call__(self, hook):
        input_seq = zip(*[item(hook) for item in self._inputs])

        input_seq = (combine_inputs(inputs) for inputs in input_seq)
        return input_seq

    def __getitem__(self, key):
        return Shortest(*[item.__getitem__(key) for item in self._inputs])

    def __repr__(self):
        res = "&".join([repr(item) for item in self._inputs])
        return f"({res})"


class Longest(Sequence):
    """Combination inputs.

    For each input field takes the right most defined value. Pads sequences
    with wait to the longest input length. An integers i is interpreted as
    wait*i.
    """
    def __init__(self, *inputs):
        super().__init__(f'Longest{inputs!r}')
        self._inputs = []
        for item in inputs:
            if isinstance(item, Longest):
                self._inputs.extend(item._inputs)
            elif isinstance(item, Sequence):
                self._inputs.append(item)
            elif isinstance(item, int):
                self._inputs.append(wait*item)
            else:
                raise AttributeError

        try:
            self.len = max([item.len for item in self._inputs])
        except ValueError:
            self.len = Length('unk')

    def __call__(self, hook):
        input_seq = zip_longest(*[item(hook) for item in self._inputs])
        input_seq = (filter(lambda x: x is not None, inputs)
                     for inputs in input_seq)

        input_seq = (combine_inputs(inputs) for inputs in input_seq)
        return input_seq

    def __getitem__(self, key):
        return Longest(*[item.__getitem__(key) for item in self._inputs])

    def __repr__(self):
        res = "|".join([repr(item) for item in self._inputs])
        return f"({res})"


def combine_inputs(inputs):
    """Combines a iterable of input states.

    Input states later in the iterable are prioritized over earlier ones.
    """
    key_list = next(wait(None)).key_list
    for inp in inputs:
        for i in range(len(key_list)):
            if inp.key_list[i] is not None:
                key_list[i] = inp.key_list[i]

    return InputState.from_list(key_list)


class Slice(Sequence):
    def __init__(self, seq, start, stop, step):
        super().__init__()

        self._seq = seq
        self.start = start
        self.stop = stop
        self.step = step

        if str(seq.len) == 'unk':
            self.len = Length('unk')
        elif seq.len == Length('inf') and stop is None:
            self.len = Length('inf')
        else:
            if stop is None:
                start, stop, step = slice(start, stop, step).indices(seq.len)
            else:
                start, stop, step = slice(start, stop, step).indices(min(seq.len, stop))

            self.len = (max(stop-start, 0)+step-1)//step

    def __call__(self, hook):
        return islice(
            self._seq(hook),
            self.start,
            self.stop,
            self.step
        )


# Creating sequences from functions


def flatten(nested):
    def wrapper(hook):
        if isinstance(nested, InputState):
            yield nested
        elif isinstance(nested, Sequence):
            yield from nested(hook)
        elif isinstance(nested, int):
            yield from (wait*nested)(None)
        else:
            for x in nested:
                yield from flatten(x)(hook)

    return wrapper


class FunctionSeq(Sequence):
    def __init__(self, fn, length=None):
        super().__init__(name=fn.__name__)
        self._fn = fn
        self.len = Length(length)

    def __call__(self, hook):
        return flatten(self._fn(hook))(hook)


def sequence(len):
    """Creates sequence from function

    fn takes one argument and returns a (nested) Sequence, InputState or int
    iterable.
    """
    def wrapper(fn):
        return FunctionSeq(fn, length=len)
    return wrapper


# More functions for sequence creation


def seq_factory(fn):
    """Sets appropriate name to created sequences

    When sequence is created its name is set to f'{fn}(*args, **kwargs)'
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        arg_list = (
            [repr(arg) for arg in args] +
            [f'{key}={repr(kwargs[key])}' for key in kwargs]
        )
        name = f"{fn.__name__}({', '.join(arg_list)})"
        seq = fn(*args, **kwargs)
        seq.name = name
        return seq
    return wrapper


@sequence(0)
def none(hook):
    """Zero length sequence
    """
    return ()


@sequence(1)
def wait(hook):
    return (InputState(),)


wait


@seq_factory
def repeat(seq):
    """Repeats sequence infinitely.
    """
    @sequence('inf')
    def fn(hook):
        while True:
            yield seq
    return fn


@seq_factory
def wait_for(func):
    @sequence('unk')
    def fn(hook):
        while not func(hook):
            yield wait
    return fn


@seq_factory
def call(function):
    @sequence(0)
    def fn(hook):
        function(hook)
        return ()
    return fn


@seq_factory
def switch(func, seq1, seq2):
    @sequence('unk')
    def fn(hook):
        if func(hook):
            for input_state in seq1:
                yield input_state
        else:
            for input_state in seq2:
                yield input_state
    return fn
