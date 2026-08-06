#include <memory>
#include <vector>

#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/joint_state.hpp"
#include "aracne_msgs/msg/leg_target.hpp"
#include "aracne_msgs/srv/compute_ik.hpp"
#include "aracne_leg_kinematics/ik_solver.hpp"

class LegKinematicsNode : public rclcpp::Node
{
public:
  LegKinematicsNode()
  : Node("leg_kinematics_node")
  {
    target_pose_subscriber_ = this->create_subscription<aracne_msgs::msg::LegTarget>(
      "/aracne/leg/target_pose",
      10,
      std::bind(&LegKinematicsNode::on_target_pose, this, std::placeholders::_1));

    joint_angles_publisher_ = this->create_publisher<sensor_msgs::msg::JointState>(
      "/aracne/leg/joint_angles", 10);

    compute_ik_service_ = this->create_service<aracne_msgs::srv::ComputeIK>(
      "/aracne/leg/compute_ik",
      std::bind(&LegKinematicsNode::on_compute_ik, this,
        std::placeholders::_1, std::placeholders::_2));

    this->declare_parameter<double>("leg_dimensions.coxa_length", 0.05);
    this->declare_parameter<double>("leg_dimensions.femur_length", 0.09);
    this->declare_parameter<double>("leg_dimensions.tibia_length", 0.11);
  }

private:
  void on_target_pose(const aracne_msgs::msg::LegTarget::SharedPtr msg)
  {
    const double l1 = this->get_parameter("leg_dimensions.coxa_length").as_double();
    const double l2 = this->get_parameter("leg_dimensions.femur_length").as_double();
    const double l3 = this->get_parameter("leg_dimensions.tibia_length").as_double();

    const auto result = aracne_leg_kinematics::solve_ik(msg->x, msg->y, msg->z, l1, l2, l3);

    if (!result.success) {
      RCLCPP_WARN(this->get_logger(), "IK failure: %s", result.error_message.c_str());
      return;
    }

    sensor_msgs::msg::JointState joint_state;
    joint_state.name = {"leg1_coxa_joint", "leg1_femur_joint", "leg1_tibia_joint"};
    joint_state.position = {result.joint_angles[0], result.joint_angles[1], result.joint_angles[2]};

    joint_angles_publisher_->publish(joint_state);
  }

  void on_compute_ik(
    const std::shared_ptr<aracne_msgs::srv::ComputeIK::Request> request,
    std::shared_ptr<aracne_msgs::srv::ComputeIK::Response> response)
  {
    const double l1 = this->get_parameter("leg_dimensions.coxa_length").as_double();
    const double l2 = this->get_parameter("leg_dimensions.femur_length").as_double();
    const double l3 = this->get_parameter("leg_dimensions.tibia_length").as_double();

    const auto result = aracne_leg_kinematics::solve_ik(request->x, request->y, request->z, l1, l2, l3);
    response->success = result.success;
    response->joint_angles = {result.joint_angles[0], result.joint_angles[1], result.joint_angles[2]};
    response->error_message = result.error_message;
  }

  rclcpp::Subscription<aracne_msgs::msg::LegTarget>::SharedPtr target_pose_subscriber_;
  rclcpp::Publisher<sensor_msgs::msg::JointState>::SharedPtr joint_angles_publisher_;
  rclcpp::Service<aracne_msgs::srv::ComputeIK>::SharedPtr compute_ik_service_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<LegKinematicsNode>());
  rclcpp::shutdown();
  return 0;
}
