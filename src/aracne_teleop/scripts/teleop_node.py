#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from aracne_msgs.msg import TeleopCmd

class TeleopNode(Node):
    def __init__(self):
        super().__init__('teleop_node')
        self.publisher_ = self.create_publisher(TeleopCmd, '/aracne/teleop/cmd', 10)
        # NOTE: no periodic timer here. The teleop must NOT drive autonomously;
        # it stays idle (does not publish) until a real operator-intent source
        # is integrated. publish_command() remains the single emission path.
        self.declare_parameter('delta_x', 0.0)
        self.declare_parameter('delta_y', 0.0)
        self.declare_parameter('delta_z', 0.0)

    def publish_command(self):
        msg = TeleopCmd()
        msg.delta_x = self.get_parameter('delta_x').value
        msg.delta_y = self.get_parameter('delta_y').value
        msg.delta_z = self.get_parameter('delta_z').value
        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = TeleopNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
