import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():

    # Package Directories
    pkg_ros_ign_gazebo = get_package_share_directory('ros_ign_gazebo')
    pkg_ros_ign_gazebo_demos = get_package_share_directory('ros_ign_gazebo_demos')

    # Parse robot description from xacro
    robot_description_file =  os.path.join(pkg_ros_ign_gazebo_demos,
        'models', 'rover.xacro')
    robot_description_config = xacro.process_file(
        robot_description_file)
    robot_description = {"robot_description": robot_description_config.toxml()}

    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='both',
        parameters=[robot_description],
    )

    # Ignition gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_ign_gazebo, 'launch', 'ign_gazebo.launch.py')),
        launch_arguments={'ign_args': '-s -r empty_physics.sdf'}.items(),
    )

    # RViz
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=[
            '-d',
            os.path.join(pkg_ros_ign_gazebo_demos, 'rviz', 'rover.rviz')
        ],
    )

    # Spawn
    spawn = Node(package='ros_ign_gazebo', executable='create',
        arguments=[
            '-name', 'rover',
            '-topic', 'robot_description',
        ],
        output='screen',
    )

    # Ign - ROS Bridge
    bridge = Node(
        package='ros_ign_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock',
            '/world/empty/model/rover/joint_state@sensor_msgs/msg/JointState[ignition.msgs.Model',
        ],
        remappings=[
            ('/world/empty/model/rover/joint_state', 'joint_states'),
        ],
        output='screen'
    )

    return LaunchDescription(
        [
            # Nodes and Launches
            gazebo,
            spawn,
            bridge,
            robot_state_publisher,
            rviz,
        ]
    )
