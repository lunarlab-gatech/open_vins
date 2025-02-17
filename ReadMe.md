# OpenVINS

[![ROS 1 Workflow](https://github.com/rpng/open_vins/actions/workflows/build_ros1.yml/badge.svg)](https://github.com/rpng/open_vins/actions/workflows/build_ros1.yml)
[![ROS 2 Workflow](https://github.com/rpng/open_vins/actions/workflows/build_ros2.yml/badge.svg)](https://github.com/rpng/open_vins/actions/workflows/build_ros2.yml)
[![ROS Free Workflow](https://github.com/rpng/open_vins/actions/workflows/build.yml/badge.svg)](https://github.com/rpng/open_vins/actions/workflows/build.yml)

## Simulate 4 Cameras

### Build
```
colcon build --event-handlers console_cohesion+ --packages-select ov_core ov_init ov_msckf ov_eval # ROS2 with verbose output
```

### Launch
```
source install/setup.bash
ros2 launch ov_msckf subscribe.launch.py config:=hilti_2022
ros2 run rviz2 rviz2 -d ov_msckf/launch/display_ros2.rviz
```

### ROS1 to ROS2 Bag Conversion
```
rosbags-convert <ros1_bag>.bag --dst <ros2_bag_folder>
```
Ref: [ROS1 to ROS2 Bag Conversion Guide](https://docs.openvins.com/dev-ros1-to-ros2.html)


### Play
```
ros2 bag play xxx
```

## Progress

<img src="https://raw.githubusercontent.com/lunarlab-gatech/open_vins/refs/heads/dev_4cams/docs/multi_cam/hilti_2022_exp04_2025-02-17_00-16-25.png"/>
