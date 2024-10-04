# Object Creator for Open Rollercoaster Tycoon 2 objects

Welcome to the project page of the OpenRCT2 Object Creator. This program is a newly developed editor that is supposed to replace Dr. J's object editor that accompanied the RCT custom scenery object (CSO) community for about 20 years.

## Installation Release Version
Just download the provided setup file and install the program. Upon first opening you need to give your OpenRCT2 installation path if you want to open `.parkobj` files that use the `.LGX` sprite storage. There will be a `config.json` file stored in `AppData/Roaming/Object Creator` that saves all your settings given. Alternatively you can download the packed zip file and unpack it anywhere you want. Note that this way you cannot open `.parkobj` files automatically via double-click.
There is also an update check included that asks you to update the program whenever there is a new version on github. When you update this way note that the update gets installed via the installer.

## Current State of Development
The program is currently under constant development. With the current version you are able to edit and create any type of Small Scenery object. Large Scenery and further object types are planned for the future.

## Feedback and Contributing
You can contribute and give feedback either through the Issues in this github or join the New Object Creator discord: [https://discord.gg/GHCP2K7d](https://discord.gg/rmdeTmKWbh)

## Installation python develop version
To run the develop version with python you need to have python installed and added to your path. Clone the repository then you need to install the following python packages to run the python code (run the following lines):

```
python -m pip install numpy
python -m pip install pyqt5
python -m pip install "Pillow<10"
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

## Mac Installation Instructions
First, clone this repository to your computer. Coders will know how to do this; if that isn't you, the easiest way to do this is to download github desktop and go to file => clone repository. Go to the URL tab and paste in https://github.com/danielmeinert/objectcreator .

I recommend cloning it in /Users/{your username}/objectcreator or similar.

Next, open a terminal window. The first thing you want to do is check you have python installed and in your path. You should, as it comes with mac! Most likely, the command:

```
python3 -h
```

Will work, giving you a list of ways to use python in the terminal. If you get "command not found", try:

```
python -h
```

Now we know the python command, we need to install the app's dependencies. Just replace python3 with python below if that was the command that worked to run python's help dialog.

```
python3 -m pip install numpy
python3 -m pip install pyqt5
python3 -m pip install Pillow<10
python3 -m pip install requests
```

Next, in the terminal, we need to install custom packages for the project. The first step is to change directories to the object creator. This depends on where you cloned the repository, but if you put it the same place as me it's going to look like:

```
cd /Users/{your username}/objectcreator
```

Just switch out {your username} for your mac username.

Next, install the app's custom pacakges:
```
python3 -m pip install -e ./customwidgets
python3 -m pip install -e ./rctobject
```

Now we're ready to run the app! But first, we need to change directories again into the object editor:
```
cd /Users/{your username}/objectcreator/editor_app
```

Then we can run it:
```
python3 app.py
```

You should now see a dialog window asking you to enter the path to OpenRCT2 first. The app doesn't need this anymore, so we can just enter /Applications.

For the default save folder, best to set that to OpenRCT2's custom content directory. You can bring that up by hitting the red scenery creator toolbox button in OpenRCT2's start-up menu, and then hitting "Open custom content folder". But it's probably this: /Users/{your username}/Library/Application Support/OpenRCT2/object . Set both the default save and default open folders to this value. Last, enter your name as the author. You may want to use the handle by which you are commonly known in the RCT community.

You should then be good to go!
