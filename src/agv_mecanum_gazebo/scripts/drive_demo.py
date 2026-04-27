#!/usr/bin/env python3
"""Drive the AGV in a square pattern to demo mecanum wheels."""
import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped


class DriveDemo(Node):
    def __init__(self):
        super().__init__('drive_demo')
        self.pub = self.create_publisher(
            TwistStamped, '/mecanum_drive_controller/reference', 10)

        # Square pattern: (linear_x, linear_y, angular_z, duration_sec)
        self.moves = [
            ( 0.3,  0.0,  0.0, 3.0),   # forward
            ( 0.0,  0.0,  0.0, 0.5),   # stop
            ( 0.0,  0.3,  0.0, 2.5),   # strafe right (mecanum!)
            ( 0.0,  0.0,  0.0, 0.5),   # stop
            (-0.3,  0.0,  0.0, 3.0),   # backward
            ( 0.0,  0.0,  0.0, 0.5),   # stop
            ( 0.0, -0.3,  0.0, 2.5),   # strafe left (mecanum!)
            ( 0.0,  0.0,  0.0, 0.5),   # stop
            ( 0.0,  0.0,  0.8, 4.0),   # rotate in place
            ( 0.0,  0.0,  0.0, 0.5),   # stop
        ]

        self.step = 0
        self.timer = self.create_timer(0.1, self.tick)
        self.start = self.get_clock().now()
        self.get_logger().info('Drive demo started — driving in a square')

    def tick(self):
        if self.step >= len(self.moves):
            self.get_logger().info('Demo complete!')
            self.timer.cancel()
            return

        lx, ly, az, dur = self.moves[self.step]
        elapsed = (self.get_clock().now() - self.start).nanoseconds / 1e9

        if elapsed >= dur:
            self.step += 1
            self.start = self.get_clock().now()
            if self.step < len(self.moves):
                self.get_logger().info(
                    f'Step {self.step}: vx={self.moves[self.step][0]:.2f} '
                    f'vy={self.moves[self.step][1]:.2f} '
                    f'wz={self.moves[self.step][2]:.2f}')
            return

        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.twist.linear.x = lx
        msg.twist.linear.y = ly
        msg.twist.angular.z = az
        self.pub.publish(msg)


def main():
    rclpy.init()
    node = DriveDemo()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
