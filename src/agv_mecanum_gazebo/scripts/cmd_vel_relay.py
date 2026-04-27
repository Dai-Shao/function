#!/usr/bin/env python3
"""Relay /cmd_vel_nav (Twist) to /model/agv_mecanum/cmd_vel for Gazebo mecanum plugin."""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class CmdVelRelay(Node):
    def __init__(self):
        super().__init__('cmd_vel_relay')
        self.pub = self.create_publisher(Twist, '/model/agv_mecanum/cmd_vel', 10)
        self.sub = self.create_subscription(Twist, '/cmd_vel_nav', self.callback, 10)
        self.get_logger().info('cmd_vel relay: /cmd_vel_nav → /model/agv_mecanum/cmd_vel')

    def callback(self, msg):
        self.pub.publish(msg)


def main():
    rclpy.init()
    node = CmdVelRelay()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
