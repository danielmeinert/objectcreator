# Object maker for Open Rollercoaster Tycoon 2 objects

To run the develop version with python, clone the repository. You need to install the following python packages to run the python code (run the following lines):

```
python3 -m pip install numpy 
python3 -m pip install pyqt5 
python3 -m pip install Pillow
```

You also need to install two custom packages of this code. Before doing this, in rctobject/rctobject/objects.py you need to change OPENRCTPATH to the path of your openrct installation (because this program extracts DAT sprites via openRCT's exportalldat command). I recommend using the -e option such that when the files in the packages get updated you don't have to reinstall them.

From inside the repo folder run

```
python3 -m pip install -e .\customwidgets\
python3 -m pip install -e .\rctobject\
```

To execute the program, go into the program's folder (either editor_app or pathgenerator_app) and run

```
python3 app.py
```







