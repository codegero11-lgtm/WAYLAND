from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_share = FindPackageShare(package='aracne_simulation')
    world_path = PathJoinSubstitution([pkg_share, 'worlds', 'mark1_lab.sdf'])

    return LaunchDescription([
        ExecuteProcess(
            cmd=['gz', 'sim', '-r', world_path],
            output='screen'
        )
    ])
