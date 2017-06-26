MoleculeX Linux Mint Environment Building Instructions

1. Install Linux Mint – Tested Version: Mate Cinnamon 17.3

2. Update repositories and packages

$ sudo apt-get update
$ sudo apt-get upgrade

3. Install Necessary Packages (Based on OpenFOAM-3.0.1)

$ sudo apt-get install build-essential flex bison cmake zlib1g-dev libboost-system-dev libboost-thread-dev libopenmpi-dev openmpi-bin gnuplot libreadline-dev libncurses-dev libxt-dev python-numpy python-pip python-scipy spyder python-dev python-qt4-gl
$ sudo apt-get install qt4-dev-tools libqt4-dev libqt4-opengl-dev freeglut3-dev libqtwebkit-dev
$ sudo apt-get install libscotch-dev libcgal-dev

4.Download OpenFOAM and ThirdParty Packages

$ cd 
$ mkdir OpenFOAM
$ cd OpenFOAM
$ wget http://downloads.sourceforge.net/foam/OpenFOAM-3.0.1.tgz
$ wget http://downloads.sourceforge.net/foam/ThirdParty-3.0.1.tgz
$ tar xzf OpenFOAM-3.0.1.tgz
$ tar xzf ThirdParty-3.0.1.tgz

4. Set Up Environment Vairables (Souce the OpenFOAM bashrc)

$ cd /etc
$ sudo gedit bash.bashrc
add source $HOME/OpenFOAM/OpenFOAM-3.0.1/etc/bashrc to the end of the text file
Open a terminal and then type “source /etc/bash.bashrc” in the current terminal window

5. Building OpenFOAM and Paraview

$ cd $WM_PROJECT_DIR
$ ./Allwmake
$ cd $WM_THIRD_PARTY_DIR
$ ./makeParaView4

6. Compiling Reader Modules

$ cd $FOAM_UTILITIES/postProcessing/graphics/PV4Readers
$ wmSET
$ ./Allwclean
$ ./Allwmake

7. Compiling LIGGGHTS DEM Enginehttps://github.com/CFDEMproject/LIGGGHTS-PUBLIC/archive/3.5.0.zip

$ cd
$ wget https://github.com/CFDEMproject/LIGGGHTS-PUBLIC/archive/3.5.0.zip
$ unzip 3.5.0.zip
$ mv LIGGGHTS-PUBLIC-3.5.0/ LIGGGHTS-PREMIUM 
$ cd LIGGGHTS-PREMIUM/src/
$ make fedora

8. Installation of LIGGGHTS

$ cd
$ sudo ln -s ~/LIGGGHTS-PREMIUM/src/lmp_fedora /usr/bin/liggghts

9. Installation of MoleculeX

$ cd
$ git clone https://github.com/mwmuni/LIGGGHTS_GUI
$ mv LIGGGHTS_GUI/ MoleculeX

10. Launchers Creation
Create Desktop Launcher for MoleculeX
Create Desktop Launcher for paraview
Add LIGGGHTS Plugins for Paraview

11. Configure MoleculeX for Connecting to LIGGGHTS and Paraview Engine
