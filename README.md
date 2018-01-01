# Dark Souls TAS tools
 
 Instructions:

- install python 3.6
- copy the project files into one folder
- navigate to that folder and launch python

```python
>>> from ds_tas.basics import *
>>> from ds_tas.scripts import glitches, menus
>>> wave = back + right + a
>>> wave.execute()
>>>
>>> glitches.moveswap_down.execute()
>>>
>>> menus.quitout.execute()
```

If you want to try the example notebook you will need to install Jupyter.
From a command terminal (where `python` will launch python 3.6)
```
> pip install jupyter
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
>>> recording.execute(skip_wait=True)
```

To try to playback the asylum run. The most likely outcome is dying to asylum demon. You might get lucky though!

Make a new game as male thief with firebombs.

Quitout without touching anything.

Execute the commands and then make sure dark souls is active before the countdown finishes.

Skip wait makes the recording load the save at the start.

```python
>>> from ds_tas.controller import KeySequence
>>>
>>> playback = KeySequence.from_file('asylum_run.txt')
>>> playback.execute(start_delay=10, skip_wait=True)
```

If you're really lucky it looks like this: https://youtu.be/gf_ApkcKt6I