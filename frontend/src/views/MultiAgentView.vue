<template>
  <div class="multi-agent-view">
    <!-- 左侧：Phaser 场景 -->
    <div class="scene-container">
      <PhaserGame ref="phaserGame" @current-active-scene="onSceneReady" />
    </div>
    
    <!-- 右侧：对话面板 -->
    <div class="chat-panel">
      <xh-card title="💬 对话记录" class="chat-card">
        <div class="messages-list">
          <div
            v-for="(msg, index) in messages"
            :key="index"
            :class="['message', `message--${msg.role}`]"
          >
            <xh-avatar
              :name="msg.agentName"
              size="sm"
            />
            <div class="message__content">
              <div class="message__header">
                <span class="message__agent">{{ msg.agentName }}</span>
                <span class="message__time">{{ formatTime(msg.timestamp) }}</span>
              </div>
              <div class="message__text">{{ msg.content }}</div>
            </div>
          </div>
        </div>
        
        <div class="chat-controls">
          <xh-button variant="primary" @click="startSimulation">
            ▶️ 开始模拟
          </xh-button>
          
          <xh-button variant="secondary" @click="resetScene">
            🔄 重置
          </xh-button>
        </div>
      </xh-card>
      
      <!-- Agent 状态面板 -->
      <xh-card title="👥 Agent 状态" class="status-card">
        <div class="agent-status-list">
          <div
            v-for="agent in agents"
            :key="agent.id"
            class="agent-status-item"
          >
            <span class="agent-avatar">{{ agent.avatar }}</span>
            <div class="agent-info">
              <span class="agent-name">{{ agent.name }}</span>
              <span class="agent-role">{{ agent.role }}</span>
            </div>
            
            <span :class="['agent-state', `state--${agent.state}`]">
              {{ agent.stateText }}
            </span>
          </div>
        </div>
      </xh-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import PhaserGame from '@/components/SimulationContainer/GameContainer/PhaserGame.vue';
import XhCard from '@/components/ui/XhCard.vue';
import XhButton from '@/components/ui/XhButton.vue';
import XhAvatar from '@/components/ui/XhAvatar.vue';

const phaserGame = ref(null);
const currentScene = ref(null);

const messages = ref([]);

const agents = ref([
  { id: 'therapist', name: '咨询师', role: 'CBT治疗师', avatar: '🧑‍⚕️', state: 'idle', stateText: '等待中' },
  { id: 'patient', name: '来访者', role: '焦虑患者', avatar: '😔', state: 'speaking', stateText: '发言中' },
  { id: 'supervisor', name: '督导', role: '督导专家', avatar: '👁️', state: 'observing', stateText: '观察中' }
]);

const onSceneReady = (scene) => {
  currentScene.value = scene;
  
  // 监听场景中的对话事件
  if (scene.events) {
    scene.events.on('agent-speech', (data) => {
      addMessage(data.agentId, data.agentName, data.content);
    });
  }
};

const addMessage = (agentId, agentName, content) => {
  const agent = agents.value.find(a => a.id === agentId);
  
  messages.value.push({
    agentId,
    agentName,
    role: agentId === 'patient' ? 'user' : 'assistant',
    content,
    timestamp: Date.now()
  });
  
  // 更新 Agent 状态
  if (agent) {
    agent.state = 'speaking';
    agent.stateText = '发言中';
    setTimeout(() => {
      agent.state = 'idle';
      agent.stateText = '等待中';
    }, 2000);
  }
};

const startSimulation = () => {
  if (currentScene.value && currentScene.value.startDialogue) {
    currentScene.value.startDialogue();
  }
  
  // 模拟添加消息到面板
  const dialogues = [
    { agentId: 'patient', agentName: '来访者', content: '我最近总是感到很焦虑...' },
    { agentId: 'therapist', agentName: '咨询师', content: '能具体说说是什么让你感到焦虑吗？' },
    { agentId: 'patient', agentName: '来访者', content: '工作压力很大，晚上睡不着。' },
    { agentId: 'supervisor', agentName: '督导', content: '注意识别是否存在灾难化思维。' },
    { agentId: 'therapist', agentName: '咨询师', content: '听起来你有很多担忧，我们一起梳理一下。' }
  ];
  
  let index = 0;
  const addNext = () => {
    if (index >= dialogues.length) return;
    const { agentId, agentName, content } = dialogues[index];
    addMessage(agentId, agentName, content);
    index++;
    setTimeout(addNext, 2500);
  };
  
  addNext();
};

const resetScene = () => {
  messages.value = [];
  if (currentScene.value && currentScene.value.resetScene) {
    currentScene.value.resetScene();
  }
};

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};
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
}

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

.message {
  display: flex;
  gap: var(--space-sm);
  padding: var(--space-sm);
  background: rgba(0, 0, 0, 0.2);
  border-radius: var(--radius-md);
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

.chat-controls {
  display: flex;
  gap: var(--space-md);
  padding: var(--space-md);
  border-top: 1px solid var(--border-color);
  justify-content: center;
}

.status-card {
  max-height: 250px;
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
}

.agent-avatar {
  font-size: 24px;
}

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
}

.agent-state {
  font-size: var(--text-xs);
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-sm);
}

.state--idle {
  background: rgba(148, 163, 184, 0.2);
  color: var(--text-muted);
}

.state--speaking {
  background: rgba(0, 212, 255, 0.2);
  color: var(--accent-primary);
}

.state--observing {
  background: rgba(56, 178, 172, 0.2);
  color: var(--accent-success);
}
</style>
