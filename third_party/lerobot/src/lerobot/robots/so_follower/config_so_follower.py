# SPDX-License-Identifier: Apache-2.0
# Copyright 2024-2025 LeRobotAI Inc.

from dataclasses import dataclass

from lerobot.robots.config import RobotConfig
from lerobot.common.datasets.lerobot_dataset import LeRobotDataset
from lerobot.common.robot_sdks.pymovebot import MoveBot


@dataclass
class SOFollowerConfig(RobotConfig):
    """Base configuration class for SO Follower robots."""

    # Robot id (required for RobotConfig)
    id: str = "so101"

    # Port to connect to the arm
    port: str = "/dev/ttyACM0"

    # Number of cameras
    # If you have more than 1 camera, use "phone", "wrist" and "overhead" as keys
    # The configuration of the camera will be loaded from the cameras config
    cameras: list[str] | None = None

    # Calibrations
    # TODO: Add automatic calibration using Dynamixel SDK
    # Format: {motor_name: {offset: float, scale: float}}
    # If you use the default SO(101) follower arm, you can find the
    # calibration in the README of the so_follower robot variant.
    # You can also use `python lerobot/scripts/calibrate.py` to compute them.
    # TODO: Add `offline_calibration` from a yaml file from a local path
    offline_calibration: dict = None

    # Use `python lerobot/scripts/calibrate.py` to compute them
    # Save them to the dataset metadata with `save_dataset_metadata`
    # They will be loaded automatically when creating the dataset
    # TODO: Add `online_calibration` from a dataset run in `lerobot/scripts/calibrate.py`
    online_calibration: dict = None

    # Number of threads to read from the cameras
    # You can increase this number if you have more than 1 camera and want to
    # decrease the latency of image capturing
    num_reader_threads: int = 1

    # Robot SDK
    # Available SDKs: "dynamixel", "pymovebot", "mock"
    # If you want to add a new SDK, check `lerobot/common/robot_sdks/`
    sdk: str = "pymovebot"

    # Pymovebot SDK configuration
    # If you have a real robot, then you probably don't need to modify these parameters
    pymovebot: MoveBot = None

    # Simulation configuration
    # TODO: Add support for simulation using MuJoCo
    # For now, this is only used for testing purposes when robot SDK is "mock"
    use_mock: bool = False

    # Maximum velocity of the robot in rad/s
    # The actions sent to the robot will be clamped to this value
    max_velocity: float = 2.0

    # Safety bounds for the robot
    # If the robot goes out of these bounds, the episode will be stopped
    # Each joint position must be between -pi and pi
    # Each joint velocity must be between -2*pi and 2*pi
    # Set to None to disable safety checks
    safety_bounds: dict = None

    def __post_init__(self):
        if self.cameras is None:
            self.cameras = ["phone"]
        if self.offline_calibration is None:
            self.offline_calibration = {}
        if self.online_calibration is None:
            self.online_calibration = {}
        if self.safety_bounds is None:
            self.safety_bounds = {
                "lower": [-3.14] * 6,
                "upper": [3.14] * 6,
                "velocity_lower": [-6.28] * 6,
                "velocity_upper": [6.28] * 6,
            }
        if self.pymovebot is None:
            self.pymovebot = MoveBot(
                port=self.port,
                use_mock=self.use_mock,
                max_velocity=self.max_velocity,
            )