# Dark Souls TAS tools
 
 Instructions:

- install python 3.6
- copy the project files into one folder
- navigate to that folder and launch python

```python
>>> from ds_tas import KeyPress, KeySequence, scripts
>>> wave = KeyPress(back=1) + KeyPress(5) + KeyPress(dpad_right=1) + KeyPress(2) + KeyPress(a=1)
>>> wave.execute
>>>
>>> scripts.moveswap_down.execute()
>>>
>>> scripts.quitout.execute()
```

If you want to try the example notebook you will need to install Jupyter.
From a command terminal (where `python` will launch python 3.6)
```
> pip install jupyter
> jupyter notebook
```

Compatible with both the latest steam release and the debug version.
