import argparse
from decimal import Decimal
from getpass import getuser
from pathlib import Path
from robotdataprocess import CoordinateFrame, ImageDataOnDisk, ImuData, OdometryData
from robotdataprocess.data_types.Data import ROSMsgLibType
from robotdataprocess.ros.RosPublisher import publish_data_ROS_multiprocess
from typing import Dict, List, Optional, Tuple


class AirMuseumOpenVINSPublisher:
    """Publishes AirMuseum's raw IMU, stereo imagery, and ground truth for OpenVINS over ROS2.

    Images are published distorted-as-recorded and unaligned to the IMU clock: OpenVINS
    undistorts internally from kalibr_imucam_chain.yaml's distortion_model/distortion_coeffs,
    and estimates the camera-IMU time offset online from its timeshift_cam_imu initial guess.
    """

    CROP_TIMES: Dict[str, Dict[str, Tuple[Decimal, Optional[Decimal]]]] = {
        "Scenario3": {
            "drone": (Decimal("0.0"), None),
            "robotA": (Decimal("0.0"), None),
            "robotB": (Decimal("0.0"), None),
            "robotC": (Decimal("0.0"), None),
        },
        "Scenario4": {
            "drone": (Decimal("0.0"), None),
            "robotA": (Decimal("0.0"), None),
            "robotB": (Decimal("0.0"), None),
            "robotC": (Decimal("0.0"), None),
        },
        "Scenario5": {
            "drone": (Decimal("0.0"), None),
            "robotA": (Decimal("0.0"), None),
            "robotB": (Decimal("0.0"), None),
            "robotC": (Decimal("0.0"), None),
        },
    }
    ROBOT_NAMES: List[str] = ["drone", "robotA", "robotB", "robotC"]
    ROBOT_LEFT_CAM_MAP: Dict[str, str] = {"drone": "cam100", "robotA": "cam101", "robotB": "cam101", "robotC": "cam101"}
    CAM_ID_TO_BAG_NAME: Dict[str, str] = {"cam100": "cam100_imu.bag", "cam101": "cam101.bag"}
    NAME_TO_FRAME_MAP: Dict[str, CoordinateFrame] = {
        "drone": CoordinateFrame.FLU, "robotA": CoordinateFrame.UFL, "robotB": CoordinateFrame.UFL, "robotC": CoordinateFrame.FUR}

    @staticmethod
    def robot_input_path(scenario: str, robot_name: str) -> Path:
        """Return one robot's raw data directory for a scenario.

        Args:
            scenario: Dataset scenario (e.g. "Scenario5").
            robot_name: Robot to look up (e.g. "drone").

        Returns:
            Path to "~/data/AirMuseum_dataset/<scenario>/data/<robot_name>".
        """
        return Path("/home") / getuser() / "data" / "AirMuseum_dataset" / scenario / "data" / robot_name

    @staticmethod
    def load_imu(scenario: str, robot_name: str) -> ImuData:
        """Load a robot's raw IMU stream from its cam100_imu bag.

        Args:
            scenario: Dataset scenario (e.g. "Scenario5").
            robot_name: Robot to load (e.g. "drone").

        Returns:
            The robot's ImuData, uncropped.
        """
        input_path: Path = AirMuseumOpenVINSPublisher.robot_input_path(scenario, robot_name)
        bag_path: Path = input_path / AirMuseumOpenVINSPublisher.CAM_ID_TO_BAG_NAME["cam100"]
        return ImuData.from_ros1_bag(bag_path, f"/{robot_name}/imu", f"{robot_name}/imu")

    @staticmethod
    def load_stereo_images(scenario: str, robot_name: str) -> Tuple[ImageDataOnDisk, ImageDataOnDisk]:
        """Load a robot's raw left/right stereo image streams.

        Args:
            scenario: Dataset scenario (e.g. "Scenario5").
            robot_name: Robot to load (e.g. "drone").

        Returns:
            (left_image_data, right_image_data), matching kalibr_imucam_chain.yaml's cam0/cam1.
        """
        input_path: Path = AirMuseumOpenVINSPublisher.robot_input_path(scenario, robot_name)
        left_cam_id: str = AirMuseumOpenVINSPublisher.ROBOT_LEFT_CAM_MAP[robot_name]
        right_cam_id: str = "cam101" if left_cam_id == "cam100" else "cam100"
        left_bag: Path = input_path / AirMuseumOpenVINSPublisher.CAM_ID_TO_BAG_NAME[left_cam_id]
        right_bag: Path = input_path / AirMuseumOpenVINSPublisher.CAM_ID_TO_BAG_NAME[right_cam_id]
        left_image_data = ImageDataOnDisk.from_ros1_bag(left_bag, f"/{robot_name}/{left_cam_id}/image_raw")
        right_image_data = ImageDataOnDisk.from_ros1_bag(right_bag, f"/{robot_name}/{right_cam_id}/image_raw")
        return left_image_data, right_image_data

    @staticmethod
    def load_ground_truth(scenario: str, robot_name: str) -> OdometryData:
        """Load a robot's ground-truth trajectory, converted to FLU and shifted to start at identity.

        Args:
            scenario: Dataset scenario (e.g. "Scenario5").
            robot_name: Robot to load (e.g. "drone").

        Returns:
            The robot's ground-truth OdometryData, uncropped.
        """
        input_path: Path = AirMuseumOpenVINSPublisher.robot_input_path(scenario, robot_name)
        ground_truth: OdometryData = OdometryData.from_txt(input_path / "body_stamped_groundtruth.txt", "world", "imu",
                                                             CoordinateFrame.NONE, True, [0, 1, 2, 3, 7, 4, 5, 6])
        ground_truth.redefine_local_axes(AirMuseumOpenVINSPublisher.NAME_TO_FRAME_MAP[robot_name], CoordinateFrame.FLU)
        ground_truth.shift_to_start_at_identity()
        return ground_truth

    @staticmethod
    def publish(scenario: str, robot_name: str) -> None:
        """Publish a robot's raw IMU, stereo images, and ground truth over ROS2 topics for OpenVINS.

        Args:
            scenario: Dataset scenario (e.g. "Scenario5").
            robot_name: Robot to publish (e.g. "drone").
        """

        # Load the data
        imu: ImuData = AirMuseumOpenVINSPublisher.load_imu(scenario, robot_name)
        left_img, right_img = AirMuseumOpenVINSPublisher.load_stereo_images(scenario, robot_name)
        ground_truth: OdometryData = AirMuseumOpenVINSPublisher.load_ground_truth(scenario, robot_name)

        # Crop the data
        start, end = AirMuseumOpenVINSPublisher.CROP_TIMES[scenario][robot_name]
        imu.crop_data(start, end)
        left_img.crop_data(start, end)
        right_img.crop_data(start, end)
        ground_truth.crop_data(start, end)

        # Publish over ROS2
        publish_data_ROS_multiprocess(
            [imu, left_img, right_img, ground_truth],
            ["/imu0", "/cam0/image_raw", "/cam1/image_raw", "/odom_gt"],
            [None, None, None, "Path"],
            [imu.get_rate_hz(), left_img.get_rate_hz(), right_img.get_rate_hz(), ground_truth.get_rate_hz()],
            [1, 3, 3, 1],
            ROSMsgLibType.RCLPY, True, verbose=True)

    @staticmethod
    def main() -> None:
        """Publish one AirMuseum robot's data for OpenVINS, per CLI arguments."""
        parser = argparse.ArgumentParser(description="Publish AirMuseum data via ROS2 topics for OpenVINS.")
        parser.add_argument("--scenario", type=str, default="Scenario5", help="Dataset scenario (e.g. Scenario5).")
        parser.add_argument("--robot_name", type=str, required=True, choices=AirMuseumOpenVINSPublisher.ROBOT_NAMES,
                             help="Robot to publish.")
        args = parser.parse_args()
        AirMuseumOpenVINSPublisher.publish(args.scenario, args.robot_name)


if __name__ == "__main__":
    AirMuseumOpenVINSPublisher.main()
