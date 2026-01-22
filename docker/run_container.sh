DATA_DIR='/media/dbutterfield3/T73'
WS_DIR='/home/dbutterfield3/Research/ros_workspaces/open_vins_ws/'

docker run -it \
    --name="open_vins" \
    --shm-size=2gb \
    --net="host" \
    --gpus="all" \
    --privileged \
    --device /dev/dri \
    --workdir="/home/$USER/open_vins_ws" \
    --env="DISPLAY=$DISPLAY" \
    --env="QT_X11_NO_MITSHM=1" \
    --env="XAUTHORITY=/tmp/.Xauthority" \
    --env="XDG_RUNTIME_DIR=/tmp/runtime-$USER" \
    --env="USER_ID=$(id -u)" \
    --env="GROUP_ID=$(id -g)" \
    --volume="$DATA_DIR:/home/$USER/data:rw" \
    --volume="$WS_DIR:/home/$USER/open_vins_ws:rw" \
    --volume="$HOME/.bash_aliases:/root/.bash_aliases" \
    --volume="$HOME/.ssh:/root/.ssh:ro" \
    --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
    --volume="/tmp/runtime-$USER:/tmp/runtime-$USER" \
    --volume="$XAUTHORITY:/tmp/.Xauthority:ro" \
    open_vins \
    /bin/bash