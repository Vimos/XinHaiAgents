<template>
  <div class="multi-agent-view">
    <!-- 左侧：Phaser 场景 / 配置上传 -->
    <div class="scene-container">
      <!-- 未加载配置时：显示上传区域 -->
      <div v-if="!simulationActive" class="upload-area">
        <div class="upload-box" @dragover.prevent @drop.prevent="handleDrop">
          <span class="upload-icon">📋</span>
          <h3>上传模拟配置</h3>
          <p>拖拽 YAML 配置文件到此处，或点击上传</p>
          <input
            ref="fileInput"
            type="file"
            accept=".yaml,.yml"
            style="display: none"
            @change="handleFileSelect"
          />
          <xh-button variant="primary" @click="$refs.fileInput.click()">
            选择配置文件
          </xh-button>
          
          <div class="example-configs">
            <p class="example-title">或选择示例配置：</p>
            <div class="example-list">
              <button class="example-btn" @click="loadExample('simple')">
                🚀 简单示例
              </button>
              <button class="example-btn" @click="loadExample('cbt')">
                🧠 CBT 心理咨询
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 已加载配置：显示 Phaser 场景 -->
      <PhaserGame v-if="simulationActive" ref="phaserGame" @current-active-scene="onSceneReady" />
    </div>
    
    <!-- 右侧：对话面板 -->
    <div class="chat-panel">
      <!-- 对话记录 -->
      <xh-card title="💬 对话记录" class="chat-card">
        <div ref="messagesList" class="messages-list">
          <div v-if="messages.length === 0 && simulationActive" class="empty-hint">
            点击「开始模拟」启动多智能体对话
          </div>
          
          <div
            v-for="(msg, index) in messages"
            :key="index"
            :class="['message', `message--${msg.role}`]"
          >
            <xh-avatar :name="msg.agentName" size="sm" />
            <div class="message__content">
              <div class="message__header">
                <span class="message__agent">{{ msg.agentName }}</span>
                <span class="message__time">{{ msg.timestamp || '' }}</span>
              </div>
              <div class="message__text" v-html="formatMarkdown(msg.content)"></div>
            </div>
          </div>
          
          <!-- 加载指示器 -->
          <div v-if="isRunning" class="message message--system">
            <div class="thinking-indicator">
              <span></span><span></span><span></span>
              <span class="thinking-text">{{ currentThinkingAgent }} 思考中...</span>
            </div>
          </div>
        </div>
        
        <div class="chat-controls">
          <xh-button 
            v-if="simulationActive && !isRunning"
            variant="primary" 
            @click="runSimulation"
            :disabled="simulationDone"
          >
            {{ simulationDone ? '✅ 模拟结束' : '▶️ 开始模拟' }}
          </xh-button>
          
          <xh-button 
            v-if="isRunning"
            variant="secondary" 
            @click="pauseSimulation"
          >
            ⏸️ 暂停
          </xh-button>
          
          <xh-button 
            v-if="simulationActive"
            variant="secondary" 
            @click="resetSimulation"
          >
            🔄 重置
          </xh-button>
          
          <xh-button 
            v-if="simulationActive"
            variant="ghost" 
            @click="clearSimulation"
          >
            📋 更换配置
          </xh-button>
        </div>
      </xh-card>
      
      <!-- Agent 状态面板 -->
      <xh-card title="👥 Agent 状态" class="status-card">
        <div v-if="!simulationActive" class="empty-status">
          上传配置后显示 Agent 信息
        </div>
        
        <div v-else class="agent-status-list">
          <div
            v-for="agent in agents"
            :key="agent.id"
            :class="['agent-status-item', { 'agent-speaking': agent.id === speakingAgentId }]"
          >
            <span class="agent-avatar">{{ getAgentAvatar(agent) }}</span>
            <div class="agent-info">
              <span class="agent-name">{{ agent.name }}</span>
              <span class="agent-role">{{ agent.role }}</span>
            </div>
            <span :class="['agent-state', `state--${agent.state || 'idle'}`]">
              {{ agent.state === 'speaking' ? '发言中' : agent.state === 'thinking' ? '思考中' : '等待中' }}
            </span>
          </div>
        </div>
        
        <!-- 拓扑信息 -->
        <div v-if="topologies.length > 0" class="topology-info">
          <div class="topology-header">📊 通信拓扑</div>
          <div class="topology-edges">
            <span v-for="(edge, i) in topologies[0].edges" :key="i" class="edge-tag">
              {{ getAgentName(edge.from) }} → {{ getAgentName(edge.to) }}
            </span>
          </div>
        </div>
      </xh-card>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue';
import { marked } from 'marked';
import PhaserGame from '@/components/SimulationContainer/GameContainer/PhaserGame.vue';
import XhCard from '@/components/ui/XhCard.vue';
import XhButton from '@/components/ui/XhButton.vue';
import XhAvatar from '@/components/ui/XhAvatar.vue';

const API_URL = 'https://chat.xinhai.co';

// ============ State ============
const phaserGame = ref(null);
const currentScene = ref(null);
const fileInput = ref(null);
const messagesList = ref(null);

const simulationActive = ref(false);
const simulationDone = ref(false);
const isRunning = ref(false);
const isPaused = ref(false);

const agents = ref([]);
const topologies = ref([]);
const messages = ref([]);
const speakingAgentId = ref(null);
const currentThinkingAgent = ref('');

// ============ 配置加载 ============

function getToken() {
  return localStorage.getItem('token') || '';
}

function getHeaders() {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getToken()}`
  };
}

async function handleFileSelect(e) {
  const file = e.target.files[0];
  if (!file) return;
  const text = await file.text();
  await createSimulation(text);
}

function handleDrop(e) {
  const file = e.dataTransfer.files[0];
  if (file && (file.name.endsWith('.yaml') || file.name.endsWith('.yml'))) {
    file.text().then(text => createSimulation(text));
  }
}

async function loadExample(name) {
  try {
    // 从仓库加载示例配置
    const res = await fetch(`/examples/${name}.yaml`);
    // 检查是否真的是 YAML 内容（不是 HTML）
    const text = await res.text();
    if (res.ok && text.trim().startsWith('arena:')) {
      // 确认是 YAML 内容
      await createSimulation(text);
    } else {
      // 如果静态文件不存在或返回 HTML，使用内置示例
      const builtinYaml = getBuiltinExample(name);
      if (builtinYaml) {
        await createSimulation(builtinYaml);
      } else {
        alert('未知示例: ' + name);
      }
    }
  } catch (e) {
    // 网络错误，使用内置示例
    const builtinYaml = getBuiltinExample(name);
    if (builtinYaml) {
      await createSimulation(builtinYaml);
    } else {
      alert('加载示例失败: ' + e.message);
    }
  }
}

function getBuiltinExample(name) {
  // 简化示例 - 只需要2个agent，不依赖外部controller
  if (name === 'simple') {
    return `arena:
  allowed_routing_types: &allowed_routing_types
    - "[Unicast]"
  prompts:
    routing_prompt: &routing_prompt |-
      你是{agent_name}。{role_description}
      历史摘要：{chat_summary}
      最新对话：{chat_history}
      可交互智能体：{agent_descriptions}
      选择通讯目标和方式，回复JSON格式：{"method": "[Unicast]", "target": [1]}
    summary_prompt: &summary_prompt |-
      根据历史摘要和最新对话，给出新的摘要。
      【历史摘要】{chat_summary}
      【最新对话】{chat_history}
      新摘要：
    prompt: &prompt |-
      【角色】{role_description}
      【摘要】{chat_summary}
      【历史】{chat_history}
      你以{routing_type}方式与{target_agent_names}通信，内容：
  name: Simple Demo
  environment:
    environment_type: agency
    environment_id: simple_demo
    controller_address: http://localhost:8000
    topologies:
      - type: agency
        name: simple
        start: 0
        max_turns: 5
        edges:
          - 0->1
          - 1->0
  agents:
    - agent_type: proxy
      agent_id: 0
      name: 用户
      role_description: 用户，提出问题和需求
      routing_prompt_template: *routing_prompt
      summary_prompt_template: *summary_prompt
      prompt_template: *prompt
      locale: zh
      allowed_routing_types: *allowed_routing_types
      llm: gpt-4o
    - agent_type: simple
      agent_id: 1
      name: 助手
      role_description: AI助手，回答用户问题
      routing_prompt_template: *routing_prompt
      summary_prompt_template: *summary_prompt
      prompt_template: *prompt
      locale: zh
      allowed_routing_types: *allowed_routing_types
      llm: gpt-4o`;
  }
  
  // 完整 CBT 示例（需要 controller 服务）
  if (name === 'cbt') {
    return `arena:
  allowed_routing_types: &allowed_routing_types
    - "[Unicast]"
  prompts:
    routing_prompt: &routing_prompt |-
      现在，你正在扮演虚拟世界中的一个智能体，名字是{agent_name}。你需要基于自己和其他智能体的关联关系做出反应。
      （1）角色描述：{role_description}
      （2）对话历史摘要：{chat_summary}
      （3）最新对话历史：{chat_history}
      （4）可以进行交互的智能体列表：{agent_descriptions}
      （5）可以采用的通讯方式有：{routing_descriptions}
      基于当前情况，选择合适的通讯目标和通讯方式。
      {{"method": "[Unicast]", "target": [1]}}
    summary_prompt: &summary_prompt |-
      请根据之前的对话摘要和新的对话内容，给出新的对话摘要。
      【历史对话摘要】{chat_summary}
      【最新对话历史】{chat_history}
      仅返回新的对话摘要内容。
    prompt: &prompt |-
      【角色描述】{role_description}
      【对话历史摘要】{chat_summary}
      【最新对话历史】{chat_history}
      现在，你选择了以{routing_type}方式与{target_agent_names}通信，请问你想发出的消息内容是什么？
  name: XinHai CBT
  environment:
    environment_type: agency
    environment_id: xinhai_cbt_simulation_0
    controller_address: http://controller:5000
    topologies:
      - type: agency
        name: cbt
        start: 0
        max_turns: 10
        edges:
          - 0->1
          - 1->0
          - 1->2
          - 2->1
  agents:
    - agent_type: proxy
      agent_id: 0
      name: 咨询者
      role_description: 咨询者，面临心理问题
      routing_prompt_template: *routing_prompt
      summary_prompt_template: *summary_prompt
      prompt_template: *prompt
      locale: zh
      allowed_routing_types: *allowed_routing_types
      llm: Qwen2.5-7B-Instruct
    - agent_type: simple
      agent_id: 1
      name: 咨询师
      role_description: 咨询师，直接和咨询者进行对话，实践认知行为疗法。
      routing_prompt_template: *routing_prompt
      summary_prompt_template: *summary_prompt
      prompt_template: *prompt
      locale: zh
      allowed_routing_types: *allowed_routing_types
      llm: Qwen2.5-7B-Instruct
    - agent_type: simple
      agent_id: 2
      name: 督导师
      role_description: 督导师，不直接和咨询者对话，为咨询师提供专业指导。
      routing_prompt_template: *routing_prompt
      summary_prompt_template: *summary_prompt
      prompt_template: *prompt
      locale: zh
      allowed_routing_types: *allowed_routing_types
      llm: Qwen2.5-7B-Instruct`;
  }
  return '';
}

async function createSimulation(configYaml) {
  try {
    const res = await fetch(`${API_URL}/api/simulation/create`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ config_yaml: configYaml })
    });
    
    if (!res.ok) {
      let errorMsg = '未知错误';
      try {
        const err = await res.json();
        errorMsg = err.detail || JSON.stringify(err);
      } catch (e) {
        errorMsg = `HTTP ${res.status}: ${res.statusText}`;
      }
      alert('创建模拟失败: ' + errorMsg);
      console.error('Simulation create failed:', res.status, errorMsg);
      return;
    }
    
    const data = await res.json();
    
    agents.value = data.agents.map(a => ({
      ...a,
      state: 'idle'
    }));
    topologies.value = data.topologies || [];
    
    simulationActive.value = true;
    simulationDone.value = false;
    messages.value = [];
    
    // 等待 Phaser 场景准备好后传递 agent 配置
    setTimeout(() => {
      if (currentScene.value && currentScene.value.setAgentsConfig) {
        currentScene.value.setAgentsConfig(data.agents);
      }
    }, 500);
    
  } catch (e) {
    alert('创建模拟失败: ' + e.message);
  }
}

// ============ 模拟控制 ============

async function runSimulation() {
  isRunning.value = true;
  isPaused.value = false;
  
  while (isRunning.value && !isPaused.value && !simulationDone.value) {
    try {
      // 标记当前思考的 agent
      const nextAgent = agents.value.find(a => a.state !== 'done');
      if (nextAgent) {
        currentThinkingAgent.value = nextAgent.name;
        nextAgent.state = 'thinking';
      }
      
      const res = await fetch(`${API_URL}/api/simulation/next`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ input_messages: [] })
      });
      
      if (!res.ok) {
        const err = await res.json();
        console.error('Simulation step failed:', err);
        break;
      }
      
      const data = await res.json();
      
      if (data.status === 'done') {
        simulationDone.value = true;
        isRunning.value = false;
        // 重置所有 agent 状态
        agents.value.forEach(a => a.state = 'idle');
        break;
      }
      
      if (data.message) {
        const msg = data.message;
        
        // 更新 agent 状态
        speakingAgentId.value = msg.senderId;
        agents.value.forEach(a => {
          if (String(a.id) === String(msg.senderId)) {
            a.state = 'speaking';
          } else {
            a.state = 'idle';
          }
        });
        
        // 添加消息
        messages.value.push({
          agentId: msg.senderId,
          agentName: msg.username,
          role: 'assistant',
          content: msg.content,
          timestamp: msg.timestamp || ''
        });
        
        scrollToBottom();
        
        // 通知 Phaser 场景
        if (currentScene.value && currentScene.value.events) {
          currentScene.value.events.emit('agent-speech', {
            agentId: msg.senderId,
            agentName: msg.username,
            content: msg.content
          });
        }
        
        // 延迟一下再执行下一步
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // 重置发言状态
        speakingAgentId.value = null;
        agents.value.forEach(a => {
          if (a.state === 'speaking') a.state = 'idle';
        });
      }
      
    } catch (e) {
      console.error('Simulation error:', e);
      break;
    }
  }
  
  isRunning.value = false;
}

function pauseSimulation() {
  isPaused.value = true;
  isRunning.value = false;
}

async function resetSimulation() {
  isRunning.value = false;
  isPaused.value = false;
  simulationDone.value = false;
  messages.value = [];
  speakingAgentId.value = null;
  agents.value.forEach(a => a.state = 'idle');
  
  try {
    await fetch(`${API_URL}/api/simulation/reset`, {
      method: 'POST',
      headers: getHeaders()
    });
  } catch (e) {
    console.error('Reset failed:', e);
  }
}

function clearSimulation() {
  isRunning.value = false;
  simulationActive.value = false;
  simulationDone.value = false;
  messages.value = [];
  agents.value = [];
  topologies.value = [];
}

// ============ Phaser ============

const onSceneReady = (scene) => {
  currentScene.value = scene;
};

// ============ 工具函数 ============

const avatarMap = {
  '咨询者': '😔', '来访者': '😔', '患者': '😔',
  '咨询师': '🧑‍⚕️', '治疗师': '🧑‍⚕️',
  '督导': '👁️', '督导师': '👁️',
};

function getAgentAvatar(agent) {
  for (const [key, emoji] of Object.entries(avatarMap)) {
    if (agent.name.includes(key)) return emoji;
  }
  return '🤖';
}

function getAgentName(id) {
  const agent = agents.value.find(a => a.id === id);
  return agent ? agent.name : `Agent-${id}`;
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesList.value) {
      messagesList.value.scrollTop = messagesList.value.scrollHeight;
    }
  });
}

marked.setOptions({ breaks: true, gfm: true });
function formatMarkdown(content) {
  if (!content) return '';
  try {
    return marked.parse(content);
  } catch (e) {
    return content.replace(/\n/g, '<br>');
  }
}
</script>

<style scoped>
.multi-agent-view {
  display: flex;
  gap: var(--space-lg);
  padding: var(--space-lg);
  height: calc(100vh - 64px);
}

.scene-container {
  flex: 2;
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 上传区域 */
.upload-area {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-xl);
}

.upload-box {
  text-align: center;
  padding: var(--space-3xl);
  border: 2px dashed rgba(0, 212, 255, 0.3);
  border-radius: var(--radius-lg);
  background: rgba(0, 212, 255, 0.05);
  transition: all 0.3s;
  max-width: 500px;
  width: 100%;
}

.upload-box:hover {
  border-color: var(--accent-primary);
  background: rgba(0, 212, 255, 0.1);
}

.upload-icon {
  font-size: 48px;
  display: block;
  margin-bottom: var(--space-lg);
}

.upload-box h3 {
  color: var(--text-primary);
  margin-bottom: var(--space-sm);
}

.upload-box p {
  color: var(--text-secondary);
  margin-bottom: var(--space-lg);
  font-size: var(--text-sm);
}

.example-configs {
  margin-top: var(--space-xl);
  padding-top: var(--space-lg);
  border-top: 1px solid var(--border-color);
}

.example-title {
  color: var(--text-muted);
  font-size: var(--text-sm);
  margin-bottom: var(--space-md);
}

.example-list {
  display: flex;
  gap: var(--space-md);
  justify-content: center;
  flex-wrap: wrap;
}

.example-btn {
  padding: var(--space-sm) var(--space-md);
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s;
}

.example-btn:hover {
  background: rgba(0, 212, 255, 0.2);
  border-color: var(--accent-primary);
  color: var(--text-primary);
}

/* 对话面板 */
.chat-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  max-width: 400px;
}

.chat-card {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.messages-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  padding: var(--space-md);
  max-height: 400px;
}

.empty-hint {
  text-align: center;
  color: var(--text-muted);
  padding: var(--space-xl);
}

.message {
  display: flex;
  gap: var(--space-sm);
  padding: var(--space-sm);
  background: rgba(0, 0, 0, 0.2);
  border-radius: var(--radius-md);
  animation: message-fade-in 0.3s ease-out;
}

@keyframes message-fade-in {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.message__content {
  flex: 1;
}

.message__header {
  display: flex;
  justify-content: space-between;
  margin-bottom: var(--space-xs);
}

.message__agent {
  font-weight: 600;
  color: var(--text-primary);
  font-size: var(--text-sm);
}

.message__time {
  color: var(--text-muted);
  font-size: var(--text-xs);
}

.message__text {
  color: var(--text-secondary);
  font-size: var(--text-sm);
  line-height: 1.5;
}

.message__text :deep(p) { margin: 2px 0; }

/* 思考指示器 */
.thinking-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: var(--space-sm);
}

.thinking-indicator span:not(.thinking-text) {
  width: 6px;
  height: 6px;
  background: var(--accent-primary);
  border-radius: 50%;
  animation: thinking-dot 1.4s ease-in-out infinite;
}

.thinking-indicator span:nth-child(2) { animation-delay: 0.2s; }
.thinking-indicator span:nth-child(3) { animation-delay: 0.4s; }

.thinking-text {
  color: var(--text-muted);
  font-size: var(--text-sm);
  margin-left: 8px;
}

@keyframes thinking-dot {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-6px); opacity: 1; }
}

.chat-controls {
  display: flex;
  gap: var(--space-sm);
  padding: var(--space-md);
  border-top: 1px solid var(--border-color);
  justify-content: center;
  flex-wrap: wrap;
}

/* Agent 状态 */
.status-card {
  max-height: 300px;
  overflow-y: auto;
}

.empty-status {
  text-align: center;
  color: var(--text-muted);
  padding: var(--space-lg);
}

.agent-status-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.agent-status-item {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-sm);
  background: rgba(0, 0, 0, 0.2);
  border-radius: var(--radius-md);
  transition: all 0.3s;
}

.agent-speaking {
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.3);
}

.agent-avatar { font-size: 24px; }

.agent-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.agent-name {
  font-weight: 600;
  color: var(--text-primary);
  font-size: var(--text-sm);
}

.agent-role {
  color: var(--text-muted);
  font-size: var(--text-xs);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 180px;
}

.agent-state {
  font-size: var(--text-xs);
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-sm);
  white-space: nowrap;
}

.state--idle {
  background: rgba(148, 163, 184, 0.2);
  color: var(--text-muted);
}

.state--speaking {
  background: rgba(0, 212, 255, 0.2);
  color: var(--accent-primary);
}

.state--thinking {
  background: rgba(255, 193, 7, 0.2);
  color: #ffc107;
}

/* 拓扑信息 */
.topology-info {
  margin-top: var(--space-md);
  padding-top: var(--space-md);
  border-top: 1px solid var(--border-color);
}

.topology-header {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--space-sm);
}

.topology-edges {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-xs);
}

.edge-tag {
  font-size: 11px;
  padding: 2px 8px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: var(--radius-sm);
  color: var(--text-muted);
}
</style>
