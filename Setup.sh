#!/bin/bash
# Proper header for a Bash script.

# Cleanup, version 2

# Run as root, of course.

echo "Starting LIGGGHTS_GUI Setup Process.........."

cd
echo "Updating PPA and dependecy packages.........."
sudo apt-get update
sudo apt-get install build-essential flex bison cmake cmake-curses-gui zlib1g-dev libboost-system-dev libboost-thread-dev libopenmpi-dev openmpi-bin gnuplot libreadline-dev libncurses-dev git libxt-dev qt4-dev-tools libqt4-dev libqt4-opengl-dev freeglut3-dev libqtwebkit-dev libscotch-dev libcgal-dev


echo "Compile and install LIGGGHTS.........."
#cd ~/LIGGGHTS_GUI/
#tar -xzvf LIGGGHTS_SOURCE.tar.gz
#cd LIGGGHTS_SOURCE/src
cd /home/user2/Desktop/Matt/Project/LIGGGHTS_GUI/LIGGGHTS_SOURCE/src
make clean
make fedora

cd

#sudo ln -s ~/LIGGGHTS_GUI/LIGGGHTS_SOURCE/src/lmp_fedora /usr/bin/lmp_gui
sudo ln -s /home/user2/Desktop/Matt/Project/LIGGGHTS_GUI/LIGGGHTS_SOURCE/src/lmp_fedora /usr/bin/lmp_gui

echo "All done!"

