import os
import pytest
import rclpy
from rclpy.node import Node
from rclpy.executors import SingleThreadedExecutor
from rclpy.qos import QoSProfile
from aracne_msgs.msg import LegTarget, TeleopCmd
from aracne_msgs.srv import ComputeIK
from sensor_msgs.msg import JointState


class TestNode(Node):
    def __init__(self):
        super().__init__('test_node')
        self.joint_state = None
        self.subscription = self.create_subscription(
            JointState,
            '/aracne/leg/joint_angles',
            self.joint_state_callback,
            QoSProfile(depth=10)
        )

    def joint_state_callback(self, msg):
        self.joint_state = msg


@pytest.fixture(scope='module')
def rclpy_node():
    rclpy.init()
    node = TestNode()
    yield node
    node.destroy_node()
    rclpy.shutdown()


def test_ik_service_reachable_point(rclpy_node):
    client = rclpy_node.create_client(ComputeIK, '/aracne/leg/compute_ik')
    assert client.wait_for_service(timeout_sec=10.0)
    request = ComputeIK.Request()
    request.x = 0.1
    request.y = 0.0
    request.z = -0.05
    future = client.call_async(request)
    rclpy.spin_until_future_complete(rclpy_node, future, timeout_sec=5.0)
    assert future.result().success
    assert len(future.result().joint_angles) == 3


def test_ik_service_unreachable_point(rclpy_node):
    client = rclpy_node.create_client(ComputeIK, '/aracne/leg/compute_ik')
    assert client.wait_for_service(timeout_sec=10.0)
    request = ComputeIK.Request()
    request.x = 0.5
    request.y = 0.0
    request.z = 0.0
    future = client.call_async(request)
    rclpy.spin_until_future_complete(rclpy_node, future, timeout_sec=5.0)
    assert not future.result().success
    assert future.result().error_message != ''


def test_target_to_joint_state_pipeline(rclpy_node):
    publisher = rclpy_node.create_publisher(LegTarget, '/aracne/leg/target_pose', 10)
    request = LegTarget()
    request.x = 0.1
    request.y = 0.0
    request.z = -0.05
    request.leg_id = 'leg1'

    timer = rclpy_node.create_timer(0.1, lambda: None)
    publisher.publish(request)

    timeout = rclpy.time.Time(seconds=5.0)
    start = rclpy.time.Time.now()
    while rclpy.time.Time.now() - start < timeout:
        rclpy.spin_once(rclpy_node, timeout_sec=0.1)
        if rclpy_node.joint_state is not None:
            break

    assert rclpy_node.joint_state is not None
    assert len(rclpy_node.joint_state.position) == 3


def test_topics_match_contract():
    node = rclpy.create_node('topic_check_node')
    topics = [name for name, _ in node.get_topic_names_and_types()]
    node.destroy_node()

    assert '/aracne/leg/target_pose' in topics
    assert '/aracne/leg/joint_angles' in topics
    assert '/aracne/teleop/cmd' in topics
