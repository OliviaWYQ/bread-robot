# 调试日志

## 2026-03-24 问题排查

### 问题描述
- 昨天（2026-03-23）校准失败
- 读取位置数据失败

### 排查环境
- 当前机器：nvidia-desktop (Ubuntu 20.04, Python 3.10.12)
- 项目位置：~/Desktop/bread-robot, ~/Desktop/lerobot-main, ~/Desktop/XLeRobot

### 排查结果

#### 1. lerobot-main 环境问题
```
$ cd ~/Desktop/lerobot-main && python -c "from lerobot.robots.so_follower import SO101Follower"
  File "<string>", line 1
    from lerobot.robots.so_follower import SO101Follower
SyntaxError: future feature annotations is not defined
```

原因：lerobot-main 使用 Python 3.11+ 语法（`type NameOrID = str | int`），当前机器 Python 3.10.12 不支持。

#### 2. XLeRobot 项目
- 路径：~/Desktop/XLeRobot/software/
- 校准方式：交互式手动校准（使用 input() 等待用户操作）
- 位置读取：通过 Dynamixel bus 的 `sync_read("Present_Position", motors)` 读取

```python
# XLeRobot/software/src/robots/xlerobot/xlerobot.py
def get_observation(self) -> dict[str, Any]:
    left_arm_pos = self.bus1.sync_read("Present_Position", self.left_arm_motors)
    right_arm_pos = self.bus2.sync_read("Present_Position", self.right_arm_motors)
    head_pos = self.bus1.sync_read("Present_Position", self.head_motors)
    # ...
```

#### 3. bread-robot 项目状态
- 当前只是一个业务规划/技术研究项目
- 包含文档：PRD、任务分解、技术选型等
- 没有实际的机器人控制代码

### 待确认
- 昨天校准是在哪个环境做的？Jetson Nano？
- 具体的错误信息是什么？

### 参考
- XLeRobot 校准代码：~/Desktop/XLeRobot/software/src/robots/xlerobot/xlerobot.py (calibrate 方法)
- LeRobot so_follower：~/Desktop/lerobot-main/lerobot/robots/so_follower.py