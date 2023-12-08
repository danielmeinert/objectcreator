# Object Creator for Open Rollercoaster Tycoon 2 objects

Welcome to the project page of the OpenRCT2 Object Creator. This program is a newly developed editor that is supposed to replace Dr. J's object editor that accompanied the RCT custom scenery object (CSO) community for about 20 years.

## Installation Release Version
Just download the provided setup file and install the program. Upon first opening you need to give your OpenRCT2 installation path if you want to open `.DAT` objects. There will be a `config.json` file stored in `AppData/Roaming/Object Creator` that saves all your settings given. Alternatively you can download the packed zip file and unpack it anywhere you want. Note that this way you cannot open `.parkobj` files automatically via double-click.
Now there is also an update check included that asks you to update the program whenever there is a new version on github. When you update this way note that the update gets installed via the installer.

## Current State of Development
The program is currently under constant development. With the first release version 0.1 you are able to edit and create simple small scenery objects. Eventually the program's scope should include all types of object types, however currently the focus is on the sprite editing part and added functionalities.

## Feedback and Contributing
You can contribute and give feedback either through the Issues in this github or join the New Object Creator discord: [https://discord.gg/GHCP2K7d](https://discord.gg/rmdeTmKWbh)

## Installation python develop version
To run the develop version with python you need to have python installed and added to your path. Clone the repository then you need to install the following python packages to run the python code (run the following lines):

```
python -m pip install numpy 
python -m pip install pyqt5 
python -m pip install Pillow<10
python -m pip install requests
```

You also need to install two custom packages of this code. 
From inside the repo folder run

```
python -m pip install -e .\customwidgets\
python -m pip install -e .\rctobject\
```

To execute the program, go into the program's folder (either editor_app or pathgenerator_app) and run

```
python app.py
```







