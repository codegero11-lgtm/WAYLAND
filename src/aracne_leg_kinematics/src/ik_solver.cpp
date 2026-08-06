#include "aracne_leg_kinematics/ik_solver.hpp"

#include <cmath>
#include <algorithm>

namespace aracne_leg_kinematics
{

static double clamp(double value, double minimum, double maximum)
{
  return std::max(minimum, std::min(value, maximum));
}

IkResult solve_ik(double x, double y, double z,
                  double l1, double l2, double l3)
{
  IkResult result;

  const double theta1 = std::atan2(y, x);
  const double r = std::sqrt(x * x + y * y) - l1;
  const double d = std::sqrt(r * r + z * z);

  if (d > (l2 + l3) || d < std::fabs(l2 - l3)) {
    result.success = false;
    result.error_message = "ponto fora do alcance";
    return result;
  }

  const double cos_theta3 = clamp((d * d - l2 * l2 - l3 * l3) / (2.0 * l2 * l3), -1.0, 1.0);
  const double theta3 = -std::acos(cos_theta3);

  const double alpha = std::atan2(z, r);
  const double cos_beta = clamp((l2 * l2 + d * d - l3 * l3) / (2.0 * l2 * d), -1.0, 1.0);
  const double beta = std::acos(cos_beta);
  const double theta2 = alpha + beta;

  result.success = true;
  result.joint_angles = {theta1, theta2, theta3};
  return result;
}

}  // namespace aracne_leg_kinematics
