# Copyright 2024 Dhairya Shah, Harsh Senjaliya

# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the “Software”), to deal 
# in the Software without restriction, including without limitation the rights to 
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies 
# of the Software, and to permit persons to whom the Software is furnished to do 
# so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all 
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription, LaunchContext
from launch.actions import DeclareLaunchArgument, RegisterEventHandler
from launch.actions import IncludeLaunchDescription, OpaqueFunction, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.event_handlers import OnProcessExit
from launch.conditions import IfCondition
from launch_ros.actions import Node

ld = LaunchDescription()

def initial(context: LaunchContext, x_pose, y_pose, namespace): 
    x_pos = context.perform_substitution(x_pose)
    y_pos = context.perform_substitution(y_pose)
    namespace_r = context.perform_substitution(namespace)

    use_sim_time = LaunchConfiguration('use_sim_time', default='True')
    package_dir = get_package_share_directory('swift_scout')
    nav_launch_dir = os.path.join(package_dir, 'launch')


    message = '{header: {frame_id: map}, pose: {pose: {position: {x: ' + \
            x_pos + ', y: ' + y_pos + \
            ', z: 0.1}, orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0000000}}, }}'
    
    name = [ '/' +  namespace_r]

    initial_pose = ExecuteProcess(
            cmd=['ros2', 'topic', 'pub', '-t', '3', '--qos-reliability', 'reliable', name + ['/initialpose'],
                'geometry_msgs/PoseWithCovarianceStamped', message],
            output='screen'
        )
    
    ld.add_action(initial_pose)

def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='True')
    package_dir = get_package_share_directory('swift_scout')
    nav_launch_dir = os.path.join(package_dir, 'launch')

    namespace_arg = DeclareLaunchArgument('namespace', default_value='tb0')
    namespace = LaunchConfiguration('namespace', default='tb0')
    x_pose_arg = DeclareLaunchArgument('x_pose', default_value='-2.0')
    x_pose = LaunchConfiguration('x_pose')
    y_pose_arg = DeclareLaunchArgument('y_pose', default_value='0.0')
    y_pose = LaunchConfiguration('y_pose')

    param_dir = LaunchConfiguration(
        'params_file',
        default=os.path.join(package_dir, 'param', 'nav2_params.yaml'))
    
    nav2 = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(nav_launch_dir, 'bringup_launch.py')),
                launch_arguments={  
                    'slam': 'False',
                    'namespace': namespace,
                    'use_namespace': 'True',
                    'map': '',
                    'map_server': 'False',
                    'params_file': param_dir,
                    'default_bt_xml_filename': os.path.join(
                        get_package_share_directory('nav2_bt_navigator'),
                        'behavior_trees', 'navigate_w_replanning_and_recovery.xml'),
                    'autostart': 'true',
                    'use_sim_time': use_sim_time, 'log_level': 'warn'
                }.items()
            )
    
    # function = OpaqueFunction(function=initial, args=[LaunchConfiguration('x_pose'), LaunchConfiguration('y_pose'), LaunchConfiguration('namespace'), LaunchConfiguration('use_rviz')])

    # spawn_nav_first = RegisterEventHandler(
    #         event_handler=OnProcessExit(
    #             target_action=nav2,
    #             on_exit=[function],
    #         )
    #     )
    
    ld = LaunchDescription()

    ld.add_action(namespace_arg)
    ld.add_action(x_pose_arg)
    ld.add_action(y_pose_arg)
    ld.add_action(nav2)
    # ld.add_action(spawn_nav_first)

    return ld
