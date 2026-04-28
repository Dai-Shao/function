# AGV 麦克纳姆轮仿真系统

基于 ROS 2 的麦克纳姆轮 AGV 仿真系统，集成 Gazebo Harmonic 物理仿真、Nav2 自主导航和 SLAM 建图功能。

## 功能特性

- **麦克纳姆轮运动学** — 全向移动控制（前后、横移、旋转）
- **Gazebo Harmonic 仿真** — 基于 ros2_control 的物理仿真环境
- **Nav2 导航** — MPPI 控制器 + NavFn 路径规划，支持自主避障导航
- **SLAM Toolbox** — 实时建图，支持在线/offline 模式
- **模块化架构** — 四个功能包解耦，便于扩展

## 包结构

```
src/
├── agv_mecanum_bringup/        # 顶层启动文件
├── agv_mecanum_description/    # 机器人 URDF/xacro 描述
├── agv_mecanum_gazebo/         # Gazebo 仿真世界与桥接
└── agv_mecanum_navigation/     # Nav2 与 SLAM 配置
```

### 包说明

**agv_mecanum_description** — 机器人模型定义
- URDF/xacro 模型，含麦克纳姆轮几何、LiDAR/IMU 传感器
- ros2_control 配置（mecanum_drive_controller）
- 关节状态广播器配置

**agv_mecanum_gazebo** — Gazebo 仿真环境
- 仓库世界场景（warehouse.world）
- ROS 2 ↔ Gazebo 桥接配置（ros_gz_bridge）
- cmd_vel 转发与 TF 中继脚本

**agv_mecanum_navigation** — 导航与建图
- Nav2 参数配置（MPPI 控制器，Omni 运动模型）
- SLAM Toolbox 配置
- RViz2 可视化配置
- 预置仓库地图

**agv_mecanum_bringup** — 系统集成
- 完整系统启动文件（仿真 + 导航）
- 纯仿真启动（不含导航）
- 键盘遥控启动

## 依赖

- ROS 2 Jazzy
- Gazebo Harmonic
- Nav2（nav2_bringup, nav2_mppi_controller）
- SLAM Toolbox
- ros2_control + gz_ros2_control
- mecanum_drive_controller
- xacro, robot_state_publisher, rviz2

## 安装

### 安装 ROS 2 与 Gazebo

```bash
# ROS 2 Jazzy（Ubuntu 24.04）
sudo apt install ros-jazzy-desktop

# Gazebo Harmonic
sudo apt install gz-harmonic

# Nav2 与 SLAM
sudo apt install ros-jazzy-nav2-bringup ros-jazzy-slam-toolbox

# ros2_control 相关
sudo apt install ros-jazzy-ros2-control ros-jazzy-ros2-controllers ros-jazzy-gz-ros2-control
```

### 编译工作空间

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
```

## 使用方法

### 1. 启动完整系统（仿真 + 导航）

```bash
ros2 launch agv_mecanum_bringup full_system.launch.py
```

启动内容：
- Gazebo 仿真环境与 AGV 模型
- Nav2 导航栈（延迟 8 秒启动，等待仿真就绪）
- RViz2 可视化界面

可选参数：
```bash
# 使用 SLAM 建图（不加载预置地图）
ros2 launch agv_mecanum_bringup full_system.launch.py use_slam:=true

# 指定地图文件
ros2 launch agv_mecanum_bringup full_system.launch.py map:=/path/to/map.yaml
```

### 2. 仅启动仿真（不含导航）

```bash
ros2 launch agv_mecanum_bringup sim_only.launch.py
```

仅启动 Gazebo 仿真，可通过遥控或直接发布 `/cmd_vel` 话题控制机器人。

### 3. 键盘遥控

```bash
ros2 launch agv_mecanum_bringup teleop.launch.py
```

使用键盘控制 AGV 移动（需在已启动仿真的情况下使用）。

## 控制接口

AGV 接收标准 `geometry_msgs/Twist` 消息（`/cmd_vel` 话题）：

| 字段 | 说明 |
|------|------|
| `linear.x` | 前后移动（正=前，负=后）|
| `linear.y` | 左右横移（正=左，负=右）— 麦克纳姆轮特有 |
| `angular.z` | 旋转（正=逆时针，负=顺时针）|

示例：
```bash
ros2 topic pub /cmd_vel geometry_msgs/Twist "{linear: {x: 0.3, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

## SLAM 建图

1. 启动系统并启用 SLAM：
   ```bash
   ros2 launch agv_mecanum_bringup full_system.launch.py use_slam:=true
   ```
2. 使用遥控或发布速度指令探索环境
3. 地图将在 RViz2 中实时显示
4. 保存地图：
   ```bash
   ros2 run nav2_map_server map_saver_cli -f ~/my_map
   ```

## 导航

1. 启动完整系统（默认加载预置仓库地图）
2. 在 RViz2 中使用 **2D Pose Estimate** 设置初始位姿
3. 使用 **Nav2 Goal** 或 **2D Goal Pose** 设置目标点
4. Nav2 自动规划路径并导航至目标

## 导航参数说明

- **控制器**：MPPI（Model Predictive Path Integral），Omni 运动模型，适配全向移动
- **规划器**：NavFn（Dijkstra/A*）
- **代价地图**：局部 4m×4m 滚动窗口 + 全局静态地图，含障碍物层和膨胀层
- **碰撞监测**：基于 LiDAR 的实时碰撞检测

## 许可证

Apache-2.0
