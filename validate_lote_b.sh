#!/bin/bash
set -e
cd /mnt/c/WAYLAND
source /opt/ros/jazzy/setup.bash
xacro src/aracne_description/urdf/aracne.xacro -o /tmp/wayland_mark1.urdf
check_urdf /tmp/wayland_mark1.urdf
