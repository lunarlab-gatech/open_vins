# OpenVINS

This is a fork of OpenVINS for use as a baseline in the Lunar Lab.

* Documentation - https://docs.openvins.com/
* Getting started guide - https://docs.openvins.com/getting-started.html

## Installation

### Docker Setup

Make sure to install:
- [Docker](https://docs.docker.com/engine/install/ubuntu/)

Then, create the ros workspace with the `src` folder, and then navigate the terminal to that `src` folder. _Creating the workspace outside the docker helps you keep your files and changes within the workspace even if you delete the un-committed docker container._ Then, clone this repository into the `src` folder.

After that, navigate to the `docker` directory. Log in to the user that you want the docker file to create in the container. Then, edit the `DOCKERFILE` to update these lines:
- `ARG USERNAME=`: Your username
- `ARG USER_UID=`: Output of `echo $UID`
- `ARG USER_GID=`: Output of `id -g`

Edit the `enter_container.sh` script with the following paths:
- `DATA_DIR=`: The directory where the HERCULES dataset is located
- `WS_DIR=`: The directory of the ROS workspace

Now, run the following commands:
```
build_container.sh
run_container.sh
```

The rest of this README **assumes that you are inside the Docker container**. For easier debugging and use, its highly recommended to install the [VSCode Docker extension](https://code.visualstudio.com/docs/containers/overview), which allows you to start/stop the container and additionally attach VSCode to the container by right-clicking on the container and selecting `Attach Visual Studio Code`. If that isn't possible, you can re-enter the container running the following command:
```
enter_container.sh
```

### Python Dependency Installation

First, navigate to the root folder of this repository (`open_vins`) and load the git submodules using the following commands:
```
git submodule init
git submodule update --init --recursive
```

Next, Install the python dependencies with the following commands:

```
cd src/open_vins_ws/dependencies/robotdataprocess/
pip install . "numpy<1.25" && pip uninstall matplotlib -y
pip install --upgrade pydantic typeguard
```

### Build 

Run the following commands:
```
cd ../../../..
colcon build 
```

## Experiments

### HERCULES dataset
To run OpenVINS on the HERCULES dataset, run the following command. The dataset sequence and robot used can be changed within the file itself:

```
tmuxp load src/open_vins/tmux/tutorial.yaml
```

## Licensing

The codebase and documentation is licensed under the [GNU General Public License v3 (GPL-3)](https://www.gnu.org/licenses/gpl-3.0.txt).
You must preserve the copyright and license notices in your derivative work and make available the complete source code with modifications under the same license ([see this](https://choosealicense.com/licenses/gpl-3.0/); this is not legal advice).

