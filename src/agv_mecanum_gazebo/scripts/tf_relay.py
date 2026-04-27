#!/usr/bin/env python3
"""Relay TF from mecanum_drive_controller/tf_odometry to /tf."""
import rclpy
from rclpy.node import Node
from tf2_msgs.msg import TFMessage


class TfRelay(Node):
    def __init__(self):
        super().__init__('tf_relay')
        self.pub = self.create_publisher(TFMessage, '/tf', 10)
        self.sub = self.create_subscription(
            TFMessage, '/mecanum_drive_controller/tf_odometry', self.callback, 10)
        self.get_logger().info('TF relay: /mecanum_drive_controller/tf_odometry → /tf')

    def callback(self, msg):
        self.pub.publish(msg)


def main():
    rclpy.init()
    node = TfRelay()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
