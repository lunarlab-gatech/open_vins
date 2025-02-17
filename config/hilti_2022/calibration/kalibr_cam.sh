rosrun kalibr kalibr_calibrate_cameras \
    --bag calib_03_2022-03-02-11-27-22.bag --target april_grid_2500x1500_7x12_15cm.yaml \
    --models pinhole-equi pinhole-equi pinhole-equi pinhole-equi \
    --topics /alphasense/cam0/image_raw /alphasense/cam1/image_raw /alphasense/cam3/image_raw /alphasense/cam4/image_raw