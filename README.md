# Dark Souls TAS tools #

Requires python 3.7 or higher.
Note: You must have an XInput controller connected.


## Examples ##

```python
'''Load a savefile, sprint forward for 2 seconds and quitout while running.'''
from ds_tas.main import *

quitout = start+5+left+a+2+up+a+2+left+a
seq = Chain(
    load,
    45,
    (run(0)&b)*60,
    repeat(run(0))&quitout
)

r(seq)
```

## Basic Inputs ##

Basic inputs directly represent a input state and last one frame.

Following basic inputs are defined:

Do Nothing:
```python
wait
```

Buttons and triggers:
```python
a, b, x, y, start, select, l1, l2, l3, r1, r2, r3
```

Mouse buttons:
```python
m1, m2, m3, m4, m5
```

DPad:
```python
up, down, left, right
```

All buttons and triggers can be specified to be unpressed byt the `~` operator. For example `~a` means that `a` is not pressed.

Raw joysticks:
```python
LeftStick(x, y), RightStick(x, y)
```
`x` and `y` are integers between -32768 and 32767 inclusive.

Joysticks from angle in radians:
```python
left_stick_rad(angle, dist), right_stick_rad(angle, dist)
```
`angle` is angle in radians, 0 is forward and pi/2 is right. `dist` is value between 0 and 1 which represents how far is the joystick from the center.

Joysticks from angle in degrees:
```python
run(angle), walk(angle), stand, right_stick(angle, distance)
```

Mouse:
```python
MouseMove(x, y), Scroll(val)
```
`MouseMove(x, y)` moves the mouse by `x` pixels horizontaly and `y` pixels vertically. `Scroll(val)` scrolls by `val` lines.

## Advanced Inputs ##

Advanced inputs do not have set value and their value is resolved at runtime usually by reading games memory. They also last one frame.

Following advanced inputs are defined:

Mouse:
```python
move_mouse_to(x_pos, y_pos), click_at(x_pos, y_pos)
```
`move_mouse_to(x_pos, y_pos)` moves the mouse to the specified position. The coordinates are pixels in 1280x720 resolution. `click_at(x_pos, y_pos)` clicks at specified position and leaves the mouse there.

Movement:
```python
arun(angle), awalk(angle), run_to(x_pos, z_pos), walk_to(x_pos, z_pos)
```
`arun` (`awalk`) runs (walks) in the specified angle regardles of current camera orientation (this is not 100% accurate and might change slightly based on camera).
`run_to` (`walk_to`) runs (walks) in the direction of specified coordinates.

## Combining inputs ##

It is possible to combine single inputs into larger input sequences.

Chaining sequences:
Sequences can be chained together using `Chain` or the `+` operator. For example `Chain(start, wait, wait, wait, wait, wait, right, a)` is equivalent to `start+wait+wait+wait+wait+wait+right+a` and opens the equipment menu.

Repeating a input:
`wait+wait+wait+wait+wait` is unnecessarly verbose so it is possible to use `wait*5` or in this case `5` instead. Another example `(a+1)*3` presses `a` 3 times and waits for a frame. Multiplying by 0 skips the sequence. It is possible to repeat a sequence infinitely using `repeat(your_sequence)`.

Combining sequences:
It is possible to execute sequences concurrently using `Shortest`, `Longest`, `&` and `|`.
All of these press a, b and left on the same frame:
```python
Shortest(a, b, left)
a & b & left
Longest(a, b, left)
a | b | left
```
If input is defined twice in the combination the right most one takes priority.
```python
run(5) & run(20) # Equivalent to run(20)
a & (~a) # Equivalent to wait
```
If sequences are longer than one frame they are combined frame by frame. `Shortest` and `&` truncates all sequences longer than the shortest one and `Longest` and `|` pads all sequences shorter than the longest one.
```python
(a+b+left) & (x+y) # Equivalent to (a&x) + (b&y)
(a+b+left) | (x+y) # Equivalent to (a&x) + (b&y) + left
```

Note an integer argument `i` for `Chain`, `Shortest` and `Longest` is equivalent to `wait*i`.

Slicing:
It is possible to slice sequences using the standart python syntax although it may have unexpected results when using auxilliary sequences.
```python
(a+b+x+y)[1:4] # Equivalent to b+x
```

## Auxilliary Sequences ##

Auxilliary sequences have length 0 which means that they cannot containe inputs, however they can have other effects.

```python
zero_mouse # Moves mouse to coordinates 0, 0 by overwriting memory.
menu_kick # Same as gadget menu kick.
reset_rng # Resets one of the random number generators used by the game. 
```

## Other Sequences ##

```python
wait_for_igt
```
Waits until igt changes.

```python
load
```
Repeatedly presses `a` and then waits for igt to start running.

```python
console_input(glob, loc)
```
Takes expressions from standart input and evaluates them in namespace passed by its arguments. Typing 'exit' exits.

## More Tools for Sequence Creation ##

`sequence(len)(fn)` takes a function that takes hook as an argument and returns any possibly nested iterable of sequences. It creates a sequence that chains all the sequences in the iterable. `len` should be a nonnegative integer, `'inf'` or `'unk'` corresponding to the length of the iterable returned by `fn`, Meant be used as a decorator for generator functions.
Examples:
```python
sequence(3)(lambda h: [a, b, x]) # Equivalent to a+b+x

@sequence(0)
def print_igt(h):
    """Print IGT
    """
    print(h.game.igt.value)
    return ()

@sequence('unk')
def spam_a(h):
    """Repeat a+wait for 3 real time seconds
    """
    from time import time
    stop = time() + 3
    while time()<stop:
        yield a+wait
```

`seq_factory` takes any function returning a sequence and gives all returned sequences a ledgible name.

Examples:
```python
@seq_factory
def wait_for(delay):
    """Waits for delay IGT seconds

    This is only an example, wait*n should be used instead
    """
    @sequence('unk')
    def fn(h)
        stop = h.game.igt.value + delay*1000
        while h.game.igt.value < stop:
            yield wait
    return fn
```
