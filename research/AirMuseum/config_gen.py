import argparse
from getpass import getuser
import numpy as np
from numpy.typing import NDArray
from pathlib import Path
from robotdataprocess import CoordinateFrame, TransformationData
from typing import Dict, List
import yaml


class AirMuseumConfigGen:
    """Generates OpenVINS kalibr_imu/imucam_chain.yaml files for AirMuseum robots.

    Inverts each camera's calibrated T_cam_imu into OpenVINS's T_imu_cam, assigns cam0/cam1 to
    whichever physical camera (cam100/cam101) is that robot's left/right, and reads IMU noise
    parameters straight from the dataset instead of hand-copying them into place.
    """

    ROBOT_NAMES: List[str] = ["drone", "robotA", "robotB", "robotC"]
    MATCH_TOLERANCE: float = 1e-9
    ROBOT_LEFT_CAM_MAP: Dict[str, str] = {"drone": "cam100", "robotA": "cam101", "robotB": "cam101", "robotC": "cam101"}
    CAM_ID_TO_CALIB_LABEL: Dict[str, str] = {"cam100": "cam0", "cam101": "cam1"}

    @staticmethod
    def fmt_matrix(M: NDArray[np.float64], indent: int = 4) -> str:
        """Format a 4x4 matrix as a multi-line YAML list, one row per line.

        Args:
            M: 4x4 matrix to format.
            indent: Number of leading spaces before each row's "- [...]".

        Returns:
            The matrix as a multi-line YAML-style string, with one row per line.
        """
        pad = " " * indent
        return "\n".join(f"{pad}- [" + ", ".join(f"{v:.17g}" for v in row) + "]" for row in M)

    @staticmethod
    def dataset_root() -> Path:
        """Return the root directory of the AirMuseum dataset."""
        return Path("/home") / getuser() / "data" / "AirMuseum_dataset"

    @staticmethod
    def calib_path_for(robot_name: str) -> Path:
        """Return the path to a robot's Kalibr stereo calibration YAML."""
        return AirMuseumConfigGen.dataset_root() / "sensors" / f"{robot_name}_cameras_calib.yaml"

    @staticmethod
    def load_calib_block(calib_path: Path, calib_label: str) -> dict:
        """Load one camera's raw block (intrinsics, distortion, resolution, ...) from the calib YAML.

        Args:
            calib_path: Path to the Kalibr stereo calibration YAML.
            calib_label: Camera block to load (e.g. "cam0").

        Returns:
            The parsed YAML block for that camera.

        Raises:
            KeyError: If calib_label is not a block in the YAML file.
        """
        with open(calib_path, "r") as f:
            data = yaml.safe_load(f)
        return data[calib_label]

    @staticmethod
    def T_imu_cam(calib_path: Path, calib_label: str) -> NDArray[np.float64]:
        """Compute OpenVINS's T_imu_cam (camera pose in IMU frame) for one calibration camera label.

        Args:
            calib_path: Path to the Kalibr stereo calibration YAML.
            calib_label: Camera block to load (e.g. "cam0").

        Returns:
            The 4x4 T_imu_cam matrix.

        Raises:
            KeyError: If calib_label or its T_cam_imu transform is not found in the YAML.
            ValueError: If the T_cam_imu transform is not a 4x4 matrix.
        """
        T_cam_imu: TransformationData = TransformationData.from_kalibr(calib_path, calib_label, "T_cam_imu", CoordinateFrame.NONE)
        return T_cam_imu.invert().as_matrix()

    @staticmethod
    def build_kalibr_imucam_yaml(robot_name: str) -> str:
        """Build the contents of a kalibr_imucam_chain.yaml for one robot's cam0(left)/cam1(right).

        Args:
            robot_name: Robot to build the file for (e.g. "drone").

        Returns:
            The full text of the kalibr_imucam_chain.yaml file.
        """
        calib_path: Path = AirMuseumConfigGen.calib_path_for(robot_name)
        left_cam_id: str = AirMuseumConfigGen.ROBOT_LEFT_CAM_MAP[robot_name]
        right_cam_id: str = "cam101" if left_cam_id == "cam100" else "cam100"

        lines: List[str] = ["%YAML:1.0", ""]
        for openvins_cam, physical_cam_id in [("cam0", left_cam_id), ("cam1", right_cam_id)]:
            calib_label = AirMuseumConfigGen.CAM_ID_TO_CALIB_LABEL[physical_cam_id]
            block: dict = AirMuseumConfigGen.load_calib_block(calib_path, calib_label)
            M: NDArray[np.float64] = AirMuseumConfigGen.T_imu_cam(calib_path, calib_label)
            lines.append(f"{openvins_cam}:")
            lines.append("  T_imu_cam:")
            lines.append(AirMuseumConfigGen.fmt_matrix(M))
            lines.append(f"  distortion_coeffs: {block['distortion_coeffs']}")
            lines.append(f"  distortion_model: {block['distortion_model']}")
            lines.append(f"  intrinsics: {block['intrinsics']}")
            lines.append(f"  resolution: {block['resolution']}")
            lines.append(f"  rostopic: /{openvins_cam}/image_raw")
            lines.append(f"  timeshift_cam_imu: {block['timeshift_cam_imu']}")
        return "\n".join(lines) + "\n"

    @staticmethod
    def build_kalibr_imu_yaml() -> str:
        """Build the contents of a kalibr_imu_chain.yaml.
        
        T_i_b, time_offset, update_rate, and model are Kalibr-schema fields OpenVINS never reads
        (see VioManagerOptions.h's "relative_config_imu" parsing), so they're omitted here.
        Tw/Ta/R_IMUtoGYRO/R_IMUtoACC/Tg (IMU intrinsics) are likewise omitted: AirMuseum's
        sensors/imu.yaml has no such calibration, and OpenVINS already falls back to
        identity/zero when they're absent.

        Returns:
            The full text of the kalibr_imu_chain.yaml file.
        """

        with open(AirMuseumConfigGen.dataset_root() / "sensors" / "imu.yaml", "r") as f:
            noise: dict = yaml.safe_load(f)
        return (
            "%YAML:1.0\n\n"
            "imu0:\n"
            f"  accelerometer_noise_density: {noise['acc_n']}  # [ m / s^2 / sqrt(Hz) ]   ( accel \"white noise\" )\n"
            f"  accelerometer_random_walk: {noise['acc_w']}    # [ m / s^3 / sqrt(Hz) ].  ( accel bias diffusion )\n"
            f"  gyroscope_noise_density: {noise['gyr_n']}      # [ rad / s / sqrt(Hz) ]   ( gyro \"white noise\" )\n"
            f"  gyroscope_random_walk: {noise['gyr_w']}        # [ rad / s^2 / sqrt(Hz) ] ( gyro bias diffusion )\n"
            "  rostopic: /imu0\n"
        )

    @staticmethod
    def config_dir_for(scenario: str, robot_name: str) -> Path:
        """Return the output config directory for one (scenario, robot) pair, creating it if needed.

        Args:
            scenario: Dataset scenario (e.g. "Scenario5").
            robot_name: Robot the config is for (e.g. "drone").

        Returns:
            Path to open_vins/config/airmuseum_<scenario>_<robot_name>.
        """
        config_dir: Path = Path(__file__).resolve().parents[2] / "config" / f"airmuseum_{scenario}_{robot_name}"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    @staticmethod
    def generate(scenario: str, robot_name: str, force: bool = False) -> List[Path]:
        """Write a robot's kalibr_imu_chain.yaml and kalibr_imucam_chain.yaml to disk.

        Args:
            scenario: Dataset scenario.
            robot_name: Robot to generate configs for (e.g. "drone").
            force: Whether to overwrite files that already exist.

        Returns:
            The paths of the files written.

        Raises:
            FileExistsError: If a target file already exists and force is False.
        """
        config_dir: Path = AirMuseumConfigGen.config_dir_for(scenario, robot_name)
        imu_path: Path = config_dir / "kalibr_imu_chain.yaml"
        imucam_path: Path = config_dir / "kalibr_imucam_chain.yaml"
        if not force:
            existing = [p for p in [imu_path, imucam_path] if p.exists()]
            if existing:
                raise FileExistsError(f"Refusing to overwrite existing file(s) (pass force=True to overwrite): {existing}")
        imu_path.write_text(AirMuseumConfigGen.build_kalibr_imu_yaml())
        imucam_path.write_text(AirMuseumConfigGen.build_kalibr_imucam_yaml(robot_name))
        return [imu_path, imucam_path]

    @staticmethod
    def verify_stereo_baseline(robot_name: str) -> List[str]:
        """Cross-check the recomputed cam1<-cam0 baseline against the calib file's own T_cn_cnm1.

        Args:
            robot_name: Robot to verify (e.g. "drone").

        Returns:
            A list of human-readable mismatch descriptions (empty if the baselines match).
        """
        calib_path: Path = AirMuseumConfigGen.calib_path_for(robot_name)
        T_cam0_imu: NDArray[np.float64] = AirMuseumConfigGen.T_imu_cam(calib_path, "cam0")
        T_cam1_imu: NDArray[np.float64] = AirMuseumConfigGen.T_imu_cam(calib_path, "cam1")
        T_cam1_cam0: NDArray[np.float64] = np.linalg.inv(T_cam1_imu) @ T_cam0_imu  # cam1<-cam0, independent of the above

        expected = np.array(AirMuseumConfigGen.load_calib_block(calib_path, "cam1")["T_cn_cnm1"], dtype=float)
        if not np.allclose(T_cam1_cam0, expected, atol=AirMuseumConfigGen.MATCH_TOLERANCE):
            return [f"{robot_name}: recomputed T_cam1_cam0 does not match calib file's T_cn_cnm1\n"
                    f"  recomputed: {T_cam1_cam0.tolist()}\n  expected:   {expected.tolist()}"]
        return []

    @staticmethod
    def main() -> None:
        """Generate kalibr_imu/imucam_chain.yaml files for one or all AirMuseum robots, then verify them."""
        parser = argparse.ArgumentParser(description="Generate OpenVINS configs for the AirMuseum dataset.")
        parser.add_argument("--scenario", type=str, default="Scenario5", help="Dataset scenario (e.g. Scenario5).")
        parser.add_argument("--robot_name", type=str, default=None, choices=AirMuseumConfigGen.ROBOT_NAMES,
                             help="Robot to generate for; defaults to all robots.")
        parser.add_argument("--force", action="store_true", help="Overwrite existing config files.")
        args = parser.parse_args()

        robot_names: List[str] = [args.robot_name] if args.robot_name else AirMuseumConfigGen.ROBOT_NAMES
        failures: List[str] = []
        for robot_name in robot_names:
            try:
                written: List[Path] = AirMuseumConfigGen.generate(args.scenario, robot_name, force=args.force)
            except FileExistsError as e:
                print(f"Skipping {robot_name}: {e}")
                continue
            for path in written:
                print(f"Wrote {path}")
            failures.extend(AirMuseumConfigGen.verify_stereo_baseline(robot_name))

        print()
        if failures:
            print("VERIFICATION FAILED:")
            for failure in failures:
                print(f"  - {failure}")
        else:
            print("VERIFICATION PASSED: recomputed stereo baselines match each calib file's T_cn_cnm1.")


if __name__ == "__main__":
    AirMuseumConfigGen.main()
