#include <gtest/gtest.h>
#include "aracne_leg_kinematics/ik_solver.hpp"

TEST(IkSolverTest, DownwardTarget)
{
  auto result = aracne_leg_kinematics::solve_ik(0.05, 0.0, -0.11, 0.05, 0.09, 0.11);
  EXPECT_TRUE(result.success);
  EXPECT_NEAR(result.joint_angles[0], 0.0, 1e-6);
}

TEST(IkSolverTest, MaximumReach)
{
  const double d = 0.09 + 0.11;
  auto result = aracne_leg_kinematics::solve_ik(0.05 + d, 0.0, 0.0, 0.05, 0.09, 0.11);
  EXPECT_TRUE(result.success);
}

TEST(IkSolverTest, UnreachableTarget)
{
  auto result = aracne_leg_kinematics::solve_ik(0.05 + 0.2, 0.0, 0.0, 0.05, 0.09, 0.11);
  EXPECT_FALSE(result.success);
  EXPECT_FALSE(result.error_message.empty());
}

TEST(IkSolverTest, NegativeTheta1)
{
  auto result = aracne_leg_kinematics::solve_ik(0.05, -0.05, -0.05, 0.05, 0.09, 0.11);
  EXPECT_TRUE(result.success);
  EXPECT_LT(result.joint_angles[0], 0.0);
}

TEST(IkSolverTest, ReferencePose)
{
  auto result = aracne_leg_kinematics::solve_ik(0.05 + 0.05, 0.0, -0.05, 0.05, 0.09, 0.11);
  EXPECT_TRUE(result.success);
}
