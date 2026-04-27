#!/usr/bin/env python3
"""Bridge /cmd_vel (Twist) to /mecanum_drive_controller/reference (TwistStamped)."""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TwistStamped


class CmdVelBridge(Node):
    def __init__(self):
        super().__init__('cmd_vel_bridge')
        self.pub = self.create_publisher(
            TwistStamped, '/mecanum_drive_controller/reference', 10)
        self.sub = self.create_subscription(
            Twist, '/cmd_vel', self.callback, 10)
        self.get_logger().info('cmd_vel bridge: /cmd_vel → /mecanum_drive_controller/reference')

    def callback(self, msg):
        stamped = TwistStamped()
        stamped.header.stamp = self.get_clock().now().to_msg()
        stamped.twist = msg
        self.pub.publish(stamped)


def main():
    rclpy.init()
    node = CmdVelBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
