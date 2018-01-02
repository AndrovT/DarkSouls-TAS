# Dark Souls TAS tools
 
 Instructions:

- install python 3.6
- Download the wheel from the releases page
- In a cmd window type `python -m pip install ds_tas-vX.X.X-cp36-cp36m-win_amd64.whl`
- Launch Python

```python
>>> from ds_tas.basics import *
>>> from ds_tas.scripts import glitches, menus
>>> wave = select + right + a
>>> wave.execute()
>>>
>>> glitches.roll_moveswap().execute()
>>>
>>> menus.quitout.execute()
```

If you want to try the example notebook you will need to install Jupyter.
From a command terminal (where `python` will launch python 3.6)
```
> python -m pip install jupyter
> jupyter notebook
```

Compatible with both the latest steam release and the debug version.

Record on first button press (wait for the counter then load a save)
```
>>> recording = KeySequence.record(start_delay=10, button_wait=True)
```

Reload the savefile and highlight the save then execute the commands.
Skip the wait for IGT to change so it can open the save.
```
>>> recording.execute(igt_wait=False)
```

To try to playback the asylum run. The most likely outcome is dying to asylum demon. You might get lucky though!

Make a new game as male thief with firebombs.

Quitout without touching anything.

Execute the commands and then make sure dark souls is active before the countdown finishes.

Setting igt_wait to False makes the playback execute the first command before waiting for IGT to change.

```python
>>> from ds_tas.controller import KeySequence
>>>
>>> playback = KeySequence.from_file('demos/asylum_run.txt')
>>> playback.execute(start_delay=10, igt_wait=False)
```

If you're really lucky it looks like this: https://youtu.be/gf_ApkcKt6I
