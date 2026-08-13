from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    simulation_share = FindPackageShare(package="aracne_simulation")
    description_share = FindPackageShare(package="aracne_description")
    bringup_share = FindPackageShare(package="aracne_bringup")

    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [simulation_share, "launch", "gazebo_mark1.launch.py"]
            )
        )
    )

    controllers_path = PathJoinSubstitution(
        [bringup_share, "config", "joint_trajectory_controller.yaml"]
    )

    robot_description = Command(
        [
            "xacro ",
            PathJoinSubstitution([description_share, "urdf", "aracne.xacro"]),
            " leg_coxa_length:=0.05",
            " leg_femur_length:=0.09",
            " leg_tibia_length:=0.11",
            " joint_limits_coxa_lower:=-1.57",
            " joint_limits_coxa_upper:=1.57",
            " joint_limits_femur_lower:=-0.78",
            " joint_limits_femur_upper:=1.57",
            " joint_limits_tibia_lower:=-2.09",
            " joint_limits_tibia_upper:=0.0",
            " controllers_file:=",
            controllers_path,
        ]
    )

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[
            {
                "robot_description": robot_description,
                "use_sim_time": True,
            }
        ],
    )

    spawn_mark1_node = Node(
        package="ros_gz_sim",
        executable="create",
        name="spawn_mark1",
        output="screen",
        parameters=[
            {
                "world": "mark1_lab",
                "name": "mark1",
                "x": 0.0,
                "y": 0.0,
                "z": 0.5,
                "Y": 0.0,
                "topic": "/robot_description",
            }
        ],
    )

    bridge_node = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="ros_gz_bridge",
        output="screen",
        parameters=[
            {
                "config_file": PathJoinSubstitution(
                    [simulation_share, "config", "bridge_mark1.yaml"]
                )
            }
        ],
    )

    leg_node = Node(
        package="aracne_leg_kinematics",
        executable="leg_kinematics_node",
        name="leg_kinematics_node",
        output="screen",
        parameters=[
            PathJoinSubstitution(
                [bringup_share, "config", "mark1_params.yaml"]
            )
        ],
    )

    teleop_node = Node(
        package="aracne_teleop",
        executable="teleop_node.py",
        name="teleop_node",
        output="screen",
    )

    teleop_bridge_node = Node(
        package="aracne_bringup",
        executable="teleop_bridge.py",
        name="teleop_bridge_node",
        output="screen",
    )

    joint_trajectory_bridge_node = Node(
        package="aracne_bringup",
        executable="joint_trajectory_bridge.py",
        name="joint_trajectory_bridge",
        output="screen",
        parameters=[
            {
                "enabled": False,
                "trajectory_duration": 2.0,
                "controller_action": (
                    "/joint_trajectory_controller/follow_joint_trajectory"
                ),
            }
        ],
    )

    spawner_node = Node(
        package="controller_manager",
        executable="spawner",
        name="controller_spawner",
        output="screen",
        arguments=["joint_trajectory_controller"],
    )

    spawner_jsb_node = Node(
        package="controller_manager",
        executable="spawner",
        name="joint_state_broadcaster_spawner",
        output="screen",
        arguments=["joint_state_broadcaster"],
    )

    return LaunchDescription(
        [
            gazebo_launch,
            TimerAction(period=3.0, actions=[robot_state_publisher_node]),
            TimerAction(period=5.0, actions=[spawn_mark1_node]),
            TimerAction(period=6.0, actions=[bridge_node]),
            TimerAction(period=7.0, actions=[spawner_jsb_node]),
            TimerAction(period=8.0, actions=[spawner_node]),
            TimerAction(
                period=9.0,
                actions=[
                    leg_node,
                    teleop_node,
                    teleop_bridge_node,
                    joint_trajectory_bridge_node,
                ],
            ),
        ]
    )

