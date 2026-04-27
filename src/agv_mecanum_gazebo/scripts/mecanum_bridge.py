#!/usr/bin/env python3
"""
Mecanum kinematics bridge: /cmd_vel (TwistStamped) → 4 Gazebo joint velocity commands.

Bypasses gz_ros2_control by directly publishing to Gazebo's native joint topics
via ros_gz_bridge. Publishes individual wheel velocities to Gazebo joint command
topics, and also publishes odometry to /odom and TF odom→base_link.
"""
import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
from std_msgs.msg import Float64
from nav_msgs.msg import Odometry
from tf2_msgs.msg import TFMessage
from geometry_msgs.msg import TransformStamped


# Mecanum kinematics parameters (must match URDF)
WHEEL_RADIUS = 0.04      # meters
LX = 0.15                # half wheelbase (x)
LY = 0.11                # half track (y)
SUM_XY = LX + LY         # 0.26


class MecanumBridge(Node):
    def __init__(self):
        super().__init__('mecanum_bridge')

        # Parameters
        self.declare_parameter('world_name', 'warehouse')
        self.declare_parameter('model_name', 'agv_mecanum')
        world = self.get_parameter('world_name').value
        model = self.get_parameter('model_name').value

        # Gazebo native joint velocity command topics
        # Pattern: /world/<world>/model/<model>/joint/<joint>/0/cmd_vel
        prefix = f'/world/{world}/model/{model}/joint'
        self.gz_topics = {
            'front_left':  f'{prefix}/front_left_wheel_joint/0/cmd_vel',
            'front_right': f'{prefix}/front_right_wheel_joint/0/cmd_vel',
            'rear_left':   f'{prefix}/rear_left_wheel_joint/0/cmd_vel',
            'rear_right':  f'{prefix}/rear_right_wheel_joint/0/cmd_vel',
        }

        # Publishers for individual wheel velocities (via ros_gz_bridge → Gazebo)
        # These publish on ROS topics which ros_gz_bridge forwards to Gazebo
        self.pubs = {}
        for name, gz_topic in self.gz_topics.items():
            self.pubs[name] = self.create_publisher(Float64, gz_topic, 10)

        # Odometry publisher
        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)

        # TF publisher
        self.tf_pub = self.create_publisher(TFMessage, '/tf', 10)

        # Subscribe to velocity commands
        self.sub = self.create_subscription(
            TwistStamped, '/mecanum_drive_controller/reference', self.cmd_cb, 10)

        # State
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.last_time = self.get_clock().now()

        self.get_logger().info(
            f'Mecanum bridge: /mecanum_drive_controller/reference → 4 Gazebo joints '
            f'(R={WHEEL_RADIUS}, lx={LX}, ly={LY})')
        for name, topic in self.gz_topics.items():
            self.get_logger().info(f'  {name}: {topic}')

    def cmd_cb(self, msg):
        now = self.get_clock().now()
        dt = (now - self.last_time).nanoseconds / 1e9
        if dt <= 0:
            dt = 0.01
        self.last_time = now

        vx = msg.twist.linear.x
        vy = msg.twist.linear.y
        wz = msg.twist.angular.z

        # Mecanum inverse kinematics → wheel angular velocities (rad/s)
        r = WHEEL_RADIUS
        fl = (1.0 / r) * (vx - vy - SUM_XY * wz)
        fr = (1.0 / r) * (vx + vy + SUM_XY * wz)
        rl = (1.0 / r) * (vx + vy - SUM_XY * wz)
        rr = (1.0 / r) * (vx - vy + SUM_XY * wz)

        # Publish wheel velocities
        self.pubs['front_left'].publish(Float64(data=fl))
        self.pubs['front_right'].publish(Float64(data=fr))
        self.pubs['rear_left'].publish(Float64(data=rl))
        self.pubs['rear_right'].publish(Float64(data=rr))

        # Forward kinematics → body velocity (for odometry)
        vxbf = (r / 4.0) * (fl + fr + rl + rr)
        vybf = (r / 4.0) * (-fl + fr + rl - rr)
        wzbf = (r / (4.0 * SUM_XY)) * (-fl + fr - rl + rr)

        # Integrate odometry
        cos_t = math.cos(self.theta)
        sin_t = math.sin(self.theta)
        self.x += (vxbf * cos_t - vybf * sin_t) * dt
        self.y += (vxbf * sin_t + vybf * cos_t) * dt
        self.theta += wzbf * dt

        # Publish odometry
        odom = Odometry()
        odom.header.stamp = now.to_msg()
        odom.header.frame_id = 'odom'
        odom.child_frame_id = 'base_link'
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.orientation.z = math.sin(self.theta / 2.0)
        odom.pose.pose.orientation.w = math.cos(self.theta / 2.0)
        odom.twist.twist.linear.x = vxbf
        odom.twist.twist.linear.y = vybf
        odom.twist.twist.angular.z = wzbf
        self.odom_pub.publish(odom)

        # Publish TF
        tf = TFMessage()
        t = TransformStamped()
        t.header.stamp = now.to_msg()
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_link'
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.rotation.z = math.sin(self.theta / 2.0)
        t.transform.rotation.w = math.cos(self.theta / 2.0)
        tf.transforms = [t]
        self.tf_pub.publish(tf)


def main():
    rclpy.init()
    node = MecanumBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
