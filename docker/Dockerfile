FROM osrf/ros:humble-desktop

# =========================================================
# =========================================================

# Are you are looking for how to use this docker file?
#   - https://docs.openvins.com/dev-docker.html
#   - https://docs.docker.com/get-started/
#   - http://wiki.ros.org/docker/Tutorials/Docker

# =========================================================
# =========================================================

# Remove old ROS 2 keys and source lists
RUN rm -f /etc/apt/sources.list.d/ros2.list \
          /etc/apt/sources.list.d/ros2-latest.list \
          /usr/share/keyrings/ros-archive-keyring.gpg \
          /usr/share/keyrings/ros2-archive-keyring.gpg

# Add the official ROS 2 key
RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
    | gpg --dearmor --batch --yes -o /usr/share/keyrings/ros2-latest-archive-keyring.gpg


# Add the ROS 2 Jammy repo using the new key
RUN echo "deb [arch=amd64 signed-by=/usr/share/keyrings/ros2-latest-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu jammy main" \
    > /etc/apt/sources.list.d/ros2.list

# Update the repo using the existing key
RUN echo "deb [signed-by=/usr/share/keyrings/ros2-latest-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu jammy main" \
    > /etc/apt/sources.list.d/ros2.list && \
    apt-get update && \
    apt-get install -y libeigen3-dev nano git

# Dependencies we use, catkin tools is very good build system
# Also some helper utilities for fast in terminal edits (nano etc)
RUN apt-get update && apt-get install -y libeigen3-dev nano git

# Ceres solver install and setup
RUN sudo apt-get install -y cmake libgoogle-glog-dev libgflags-dev libatlas-base-dev libeigen3-dev libsuitesparse-dev libceres-dev
# ENV CERES_VERSION="2.0.0"
# RUN git clone https://ceres-solver.googlesource.com/ceres-solver && \
#     cd ceres-solver && \
#     git checkout tags/${CERES_VERSION} && \
#     mkdir build && cd build && \
#     cmake .. && \
#     make -j$(nproc) install && \
#     rm -rf ../../ceres-solver

# Seems this has Python 3.10 installed on it...
RUN apt-get update && apt-get install -y python3-dev python3-matplotlib python3-numpy python3-psutil python3-tk

# Install deps needed for clion remote debugging
# https://blog.jetbrains.com/clion/2020/01/using-docker-with-clion/
# RUN sed -i '6i\source "/catkin_ws/install/setup.bash"\' /ros_entrypoint.sh
RUN apt-get update && apt-get install -y ssh build-essential gcc g++ \
    gdb clang cmake rsync tar python3 && apt-get clean
RUN ( \
    echo 'LogLevel DEBUG2'; \
    echo 'PermitRootLogin yes'; \
    echo 'PasswordAuthentication yes'; \
    echo 'Subsystem sftp /usr/lib/openssh/sftp-server'; \
  ) > /etc/ssh/sshd_config_test_clion \
  && mkdir /run/sshd
RUN useradd -m user && yes password | passwd user
RUN usermod -s /bin/bash user
CMD ["/usr/sbin/sshd", "-D", "-e", "-f", "/etc/ssh/sshd_config_test_clion"]

# Set user arguments (being username, echo $UID, and id -g)
ARG USERNAME=dbutterfield3
ENV USERNAME=${USERNAME}
ARG USER_UID=3332128
ARG USER_GID=2626

# Create a non-root user with matching UID/GID
RUN groupadd --gid ${USER_GID} ${USERNAME} && \
    useradd --uid ${USER_UID} --gid ${USER_GID} -m ${USERNAME} && \
    usermod -aG sudo ${USERNAME} && \
    echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

#Add a custom .bashrc with warm colors and fixed hostname
RUN echo 'export PS1="\\[\\e[1;31m\\]\\u@open_vins_ros\\[\\e[0m\\]:\\[\\e[1;33m\\]\\w\\[\\e[0m\\]\\$ "' > /home/${USERNAME}/.bashrc && \
    chown ${USERNAME}:${USERNAME} /home/${USERNAME}/.bashrc

# Set default user
USER ${USERNAME}
WORKDIR /home/${USERNAME}
SHELL ["/bin/bash", "-c"]

# Disable the sudo warning message on terminal open
RUN sudo echo ""

# Install tmuxp 
RUN sudo apt update
RUN sudo apt install tmux tmuxp -y
RUN touch ~/.tmux.conf && \
    echo "set -g mouse on" >> ~/.tmux.conf

# Install additional ROS utilities
RUN sudo apt install ros-humble-rqt-graph ros-humble-rviz-imu-plugin -y

# Source ROS2 environment for the user
RUN echo "source /opt/ros/humble/setup.bash" >> /home/${USERNAME}/.bashrc

# Install Boost & image_transport
RUN sudo apt install libboost-all-dev ros-humble-image-transport ros-humble-cv-bridge ros-humble-rviz2 -y

# Install additional plugins for rqt
RUN sudo apt install ros-humble-rqt-* -y