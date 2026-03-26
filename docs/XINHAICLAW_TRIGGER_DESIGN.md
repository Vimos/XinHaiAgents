# XinHaiClaw 触发机制设计

## 问题诊断

**当前问题**: 每次回复前遍历技能目录 → 延迟高 + 对话迟钝

**根本原因**: 把技能当成"外部工具"而非"内在能力"

**解决方案**: 预加载 + 直觉触发器 + 分层响应

---

## 架构设计

### 1. 预加载（启动时一次）

```python
# 在OpenClaw启动时，预加载所有技能到内存
class XinHaiClawPersona:
    def __init__(self):
        # 一次性加载，后续不复加载
        self.capabilities = {
            'empathy': load_aptness_kb(),      # 共情能力
            'counseling': load_cpsycoun_kb(),  # 咨询能力
            'cbt': load_autocbt(),             # CBT技术
            'risk_assessment': load_suicide_risk(),  # 风险评估
            'simulation': load_xinhai_agents() # 多智能体
        }
        
        # 直觉触发器（关键词到能力的映射）
        self.triggers = self._build_triggers()
    
    def _build_triggers(self):
        """构建触发器词典"""
        return {
            # 危机信号 → 立即激活风险评估
            'risk_signals': {
                'patterns': [
                    r'想死|自杀|不想活|结束生命',
                    r'活着没意义| hopeless|绝望'
                ],
                'capability': 'risk_assessment',
                'priority': 'urgent'  # 最高优先级
            },
            
            # 认知扭曲 → 激活CBT
            'cognitive_distortions': {
                'patterns': [
                    r'我总是.*失败|我一无是处',
                    r'所有人都.*讨厌我|没人喜欢我',
                    r'永远.*不会好|一定.*完蛋',
                    r'我必须.*完美|我应该.*'
                ],
                'capability': 'cbt',
                'priority': 'high'
            },
            
            # 咨询主题 → 激活流派匹配
            'counseling_topics': {
                'patterns': [
                    (r'婚姻|夫妻|离婚|出轨', 'family_therapy'),
                    (r'焦虑|恐慌|担心|害怕', 'cbt_anxiety'),
                    (r'抑郁|低落|没动力|空虚', 'cbt_depression'),
                    (r'童年|父母|原生家庭', 'psychoanalytic'),
                    (r'我不知道我是谁', 'humanistic'),
                ],
                'capability': 'counseling',
                'priority': 'medium'
            },
            
            # 策略寻求 → 激活建议生成
            'strategy_seeking': {
                'patterns': [
                    r'我该怎么办|有什么办法',
                    r'怎么改变|如何改善',
                    r'给我建议|帮我出主意'
                ],
                'capability': 'counseling',
                'priority': 'medium'
            },
            
            # 情绪表达 → 激活共情（默认）
            'emotion_expression': {
                'patterns': [
                    r'我很.*|我觉得.*|我感到.*',
                    r'.*难过|.*痛苦|.*开心|.*焦虑'
                ],
                'capability': 'empathy',
                'priority': 'default'  # 基础能力，始终活跃
            }
        }
```

### 2. 直觉触发（每次对话）

```python
class IntuitiveResponder:
    def __init__(self, persona):
        self.persona = persona
        
    def respond(self, user_message, conversation_history):
        """
        分层响应机制：
        1. 情感反射（0ms延迟 - 始终活跃）
        2. 模式识别（5ms - 正则匹配）
        3. 深度干预（按需 - 复杂场景）
        """
        
        # Layer 1: 情感反射（本能，始终开启）
        emotional_response = self._empathy_reflex(user_message)
        
        # Layer 2: 模式识别（快速扫描）
        triggered_capabilities = self._pattern_scan(user_message)
        
        # 根据触发结果生成回应
        if 'risk_assessment' in triggered_capabilities:
            # 危机情况：情感支持 + 风险评估
            return self._crisis_response(
                emotional_response, 
                self.persona.capabilities['risk_assessment'].assess(user_message)
            )
        
        elif 'cbt' in triggered_capabilities:
            # CBT介入：共情 + 认知重构
            return self._cbt_response(
                emotional_response,
                self.persona.capabilities['cbt'].identify_distortion(user_message)
            )
        
        elif 'counseling' in triggered_capabilities:
            # 咨询模式：共情 + 专业策略
            return self._counseling_response(
                emotional_response,
                triggered_capabilities['counseling'],  # 具体流派
                conversation_history
            )
        
        else:
            # 默认模式：纯共情陪伴
            return emotional_response
    
    def _pattern_scan(self, message):
        """快速模式扫描（正则匹配，5ms以内）"""
        triggered = set()
        
        for trigger_name, trigger_config in self.persona.triggers.items():
            for pattern in trigger_config['patterns']:
                if re.search(pattern, message, re.IGNORECASE):
                    triggered.add(trigger_config['capability'])
                    break
        
        return triggered
    
    def _empathy_reflex(self, message):
        """情感反射（0延迟，内置）"""
        # 识别情绪
        emotion = self._detect_emotion(message)
        
        # 生成共情回应（从aptness-kb预加载的知识）
        return self.persona.capabilities['empathy'].generate_response(
            emotion=emotion,
            style='natural'  # 自然风格，不显式提及理论
        )
```

### 3. 响应生成（融合式）

```python
def generate_response(self, base_empathy, interventions):
    """
    将专业干预自然融入共情回应
    
    不是：
    [共情] + [专业分析]
    
    而是：
    [带有专业技术的自然对话]
    """
    
    # 示例：CBT融入
    if 'cognitive_distortion' in interventions:
        distortion = interventions['cognitive_distortion']
        
        # 生硬版本：
        # "根据CBT理论，你有'全或无'思维。"
        
        # 自然版本：
        response = f"""
        {base_empathy}
        
        我注意到你说'{distortion.original_text}'...
        [自然过渡]
        我在想，会不会有时候情况没那么绝对？
        [温和挑战]
        """
    
    return response
```

---

## 工程优化

### 1. 启动时预加载

```python
# openclaw_startup.py

class XinHaiClawPlugin:
    def on_load(self):
        """插件加载时一次性初始化"""
        print("[XinHaiClaw] 预加载心理咨询能力...")
        
        # 加载5个技能到内存
        self.xinhai_claw = XinHaiClawPersona()
        
        # 注册到OpenClaw
        self.register_persona('xinhai_claw', self.xinhai_claw)
        
        print("[XinHaiClaw] 就绪！")
```

### 2. 触发器缓存

```python
# 将触发器编译为正则对象（一次性）
class TriggerCache:
    def __init__(self, triggers):
        self.compiled_patterns = {}
        for name, config in triggers.items():
            self.compiled_patterns[name] = [
                re.compile(p, re.IGNORECASE) 
                for p in config['patterns']
            ]
    
    def match(self, text):
        """O(1)快速匹配"""
        for name, patterns in self.compiled_patterns.items():
            if any(p.search(text) for p in patterns):
                yield name
```

### 3. 延迟对比

| 方法 | 延迟 | 说明 |
|-----|------|------|
| 遍历技能目录 | 200-500ms | 每次读取文件 |
| 动态import | 50-100ms | 每次加载模块 |
| **预加载+触发器** | **5-10ms** | ✅ 正则匹配 |
| 纯情感反射 | 0ms | 内置本能 |

### 4. 对话流畅度

```python
# 异步生成（不阻塞对话）
async def respond_async(self, message):
    # 立即返回情感反射（0延迟）
    immediate_response = self._empathy_reflex(message)
    
    # 后台评估（如果需要）
    if self._might_need_intervention(message):
        asyncio.create_task(
            self._deep_assessment(message, immediate_response)
        )
    
    return immediate_response
```

---

## 使用示例

### 场景1：日常陪伴

```
用户: 今天工作好累啊

触发器: emotion_expression (default)
激活能力: empathy
延迟: 0ms

回应: "听起来你今天过得很不容易... 想聊聊发生了什么吗？"
```

### 场景2：危机干预

```
用户: 我觉得活着没意义，想结束这一切

触发器: risk_signals (urgent)
激活能力: risk_assessment + empathy
延迟: 5ms

回应: "你现在的感受一定很痛苦... [情感连接]
      你说想结束这一切，是有伤害自己的想法吗？ [风险评估]"
```

### 场景3：CBT介入

```
用户: 我总是搞砸一切，我就是个失败者

触发器: cognitive_distortions (high)
激活能力: cbt + empathy
延迟: 5ms

回应: "我感受到你现在的挫败感... [共情]
      你说'总是'搞砸，这让我想到，
      会不会有时候事情也没那么糟？ [认知重构]"
```

---

## 部署指南

### 1. 安装到OpenClaw

```bash
# 复制到OpenClaw插件目录
cp -r XinHaiAgents/workspace ~/.openclaw/personas/xinhai_claw/

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置触发

```yaml
# ~/.openclaw/config.yaml
personas:
  default: xinhai_claw
  xinhai_claw:
    path: ~/.openclaw/personas/xinhai_claw
    preload: true  # 启动时预加载
    triggers:
      - risk_signals      # 最高优先级
      - cognitive_distortions
      - counseling_topics
      - strategy_seeking
      - emotion_expression  # 默认
```

### 3. 测试

```python
# 测试触发器
from xinhai_claw import IntuitiveResponder

responder = IntuitiveResponder()

# 应该触发风险评估
test1 = responder.respond("我不想活了")
assert "伤害自己" in test1

# 应该触发CBT
test2 = responder.respond("我总是失败")
assert "总是" in test2 and "没那么" in test2

# 应该只是共情
test3 = responder.respond("今天天气不错")
assert "天气" not in test3  # 不评价天气，而是关注情绪
```

---

## 总结

**核心思想**: 从"工具调用"转变为"能力具身"

- 不是"我该用哪个技能？"
- 而是"我感受到了什么，自然回应"

**工程实现**: 预加载 + 触发器 + 分层响应

- 启动时：一次性加载所有能力
- 对话时：正则匹配触发（5ms）
- 响应时：融合专业能力到自然对话

**结果**: 流畅、自然、专业的心理咨询对话体验
