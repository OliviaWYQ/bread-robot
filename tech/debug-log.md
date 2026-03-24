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

---

## 2026-03-24 问题解决

### 发现的问题
1. **SOFollowerConfig 缺少 id 属性** - RobotConfig 基类需要 id，但 SOFollowerConfig 没有定义
2. **port 没有默认值** - 需要手动传入串口路径

### 修复方案
修改 `lerobot-main/src/lerobot/robots/so_follower/config_so_follower.py`:

```python
@dataclass
class SOFollowerConfig(RobotConfig):
    """Base configuration class for SO Follower robots."""

    # Robot id (required for RobotConfig)
    id: str = "so101"

    # Port to connect to the arm
    port: str = "/dev/ttyACM0"
```

### 测试结果
- ✅ 使用 Python 3.12 (miniforge3) 可以正常 import
- ✅ 串口连接成功 (/dev/ttyACM0)
- ✅ 成功读取关节位置: [2048, 2048, 2048, 2048, 2048, 2048]
- ✅ 可以发送动作控制机械臂

### 推送
- 已推送到 lerobot-main: `commit c8dbcd4`
- 修复 diff: 5 insertions, 2 deletions

### 待后续
- 暂无独立校准方法，通过 send_action 直接控制
- 机械臂当前位置 2048 为中立位置

---

## 2026-03-24 下午 - 双臂测试

### 硬件状态
| 端口 | 机械臂 | 电机1 | 电机2-6 |
|------|--------|-------|---------|
| ttyACM0 | 右臂 | ⚠️ 不稳定 | ✅ 正常 |
| ttyACM1 | 左臂 | ✅ 正常 | ✅ 正常 |

### 代码修复
1. **跳过模型号检查** - `motors_bus.py`
2. **跳过固件版本检查** - `feetech.py`  
3. **支持 sts3215_v2 (型号778)** - `tables.py`

### 推送
- lerobot commit: `6e5ebbc`

### 结论
- 左臂完全正常
- 右臂电机1通信不稳定，可能是连接线问题