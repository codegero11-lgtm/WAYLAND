#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from aracne_msgs.msg import TeleopCmd, LegTarget


class TeleopBridge(Node):
    def __init__(self):
        super().__init__('teleop_bridge')
        self.subscription = self.create_subscription(
            TeleopCmd,
            '/aracne/teleop/cmd',
            self.on_teleop_cmd,
            10)
        self.publisher = self.create_publisher(LegTarget, '/aracne/leg/target_pose', 10)

    def on_teleop_cmd(self, msg):
        target = LegTarget()
        target.x = msg.delta_x
        target.y = msg.delta_y
        target.z = msg.delta_z
        target.leg_id = 'leg1'
        self.publisher.publish(target)


def main(args=None):
    rclpy.init(args=args)
    node = TeleopBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
