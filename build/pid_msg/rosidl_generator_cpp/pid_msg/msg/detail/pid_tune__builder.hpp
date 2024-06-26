// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from pid_msg:msg/PidTune.idl
// generated code does not contain a copyright notice

#ifndef PID_MSG__MSG__DETAIL__PID_TUNE__BUILDER_HPP_
#define PID_MSG__MSG__DETAIL__PID_TUNE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "pid_msg/msg/detail/pid_tune__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace pid_msg
{

namespace msg
{

namespace builder
{

class Init_PidTune_ki
{
public:
  explicit Init_PidTune_ki(::pid_msg::msg::PidTune & msg)
  : msg_(msg)
  {}
  ::pid_msg::msg::PidTune ki(::pid_msg::msg::PidTune::_ki_type arg)
  {
    msg_.ki = std::move(arg);
    return std::move(msg_);
  }

private:
  ::pid_msg::msg::PidTune msg_;
};

class Init_PidTune_kd
{
public:
  explicit Init_PidTune_kd(::pid_msg::msg::PidTune & msg)
  : msg_(msg)
  {}
  Init_PidTune_ki kd(::pid_msg::msg::PidTune::_kd_type arg)
  {
    msg_.kd = std::move(arg);
    return Init_PidTune_ki(msg_);
  }

private:
  ::pid_msg::msg::PidTune msg_;
};

class Init_PidTune_kp
{
public:
  Init_PidTune_kp()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_PidTune_kd kp(::pid_msg::msg::PidTune::_kp_type arg)
  {
    msg_.kp = std::move(arg);
    return Init_PidTune_kd(msg_);
  }

private:
  ::pid_msg::msg::PidTune msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::pid_msg::msg::PidTune>()
{
  return pid_msg::msg::builder::Init_PidTune_kp();
}

}  // namespace pid_msg

#endif  // PID_MSG__MSG__DETAIL__PID_TUNE__BUILDER_HPP_
