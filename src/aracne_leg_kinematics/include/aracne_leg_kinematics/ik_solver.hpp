#ifndef ARACNE_LEG_KINEMATICS_IK_SOLVER_HPP_
#define ARACNE_LEG_KINEMATICS_IK_SOLVER_HPP_

#include <string>
#include <array>

namespace aracne_leg_kinematics
{

struct IkResult
{
  bool success{false};
  std::array<double, 3> joint_angles{{0.0, 0.0, 0.0}};
  std::string error_message;
};

IkResult solve_ik(double x, double y, double z,
                  double l1, double l2, double l3);

}

#endif  // ARACNE_LEG_KINEMATICS_IK_SOLVER_HPP_
