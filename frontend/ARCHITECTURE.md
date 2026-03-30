# XinHaiAgents 新前端架构

## 核心设计原则

### 1. 每个页面独立 Chat 实例
- 每个 Vue 页面使用独立的 `useChat()` 组合式函数实例
- 通过 `sidebar` 参数区分不同页面的对话（chat/cbt/empathy/simulation）
- 对话历史自动按 sidebar 隔离，互不干扰

### 2. 统一 API 层
所有后端通信集中在 `api/index.js`：
```javascript
import { authApi, chatApi, simulationApi } from '@/api/index.js'

// 认证
await authApi.login(credentials)

// 对话
await chatApi.sendMessage({ messages, sidebar, onChunk: ... })
await chatApi.getHistory(sidebar)
await chatApi.saveSession({ sessionKey, sidebar, title, messages })

// 模拟
await simulationApi.create(configYaml)
await simulationApi.next()
```

### 3. 状态管理简化
- 不使用复杂的 Pinia store
- 每个页面使用 `useChat()` 管理自己的状态
- 状态清晰、可预测、易调试

## 目录结构

```
frontend/src/
├── api/
│   └── index.js              # 统一 API 层
├── composables/
│   └── useChat.js            # 对话逻辑复用
├── components/
│   └── ChatPanel.vue         # 通用对话面板
└── views/
    ├── NewChatView.vue       # Chat 页面示例
    ├── NewCBTView.vue        # CBT 页面示例
    ├── NewEmpathyView.vue    # Empathy 页面示例
    └── ...                   # 其他页面按同样模式
```

## 使用方式

### 创建新页面

```vue
<template>
  <div class="my-view">
    <ChatPanel
      :messages="chat.messages.value"
      :is-loading="chat.isLoading.value"
      :sessions="chat.sessions.value"
      show-sidebar
      @send="handleSend"
      @new-chat="chat.createNewSession"
      @select-session="chat.loadSession"
    />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useChat } from '@/composables/useChat.js'
import ChatPanel from '@/components/ChatPanel.vue'

const SIDEBAR = 'my_feature'  // 独立的 sidebar 标识
const chat = useChat(SIDEBAR, '页面标题')

function handleSend(message) {
  chat.sendMessage(message)
}

onMounted(() => {
  chat.init()  // 加载历史或创建新会话
})
</script>
```

### 添加路由

```javascript
// router.js
import NewChatView from '@/views/NewChatView.vue'
import NewCBTView from '@/views/NewCBTView.vue'
import NewEmpathyView from '@/views/NewEmpathyView.vue'

const routes = [
  { path: '/chat', component: NewChatView, meta: { requiresAuth: true } },
  { path: '/cbt', component: NewCBTView, meta: { requiresAuth: true } },
  { path: '/empathy', component: NewEmpathyView, meta: { requiresAuth: true } },
]
```

## useChat API

### State (响应式)
- `sessionKey` - 当前会话标识
- `messages` - 消息列表
- `isLoading` - 是否正在发送/接收
- `error` - 错误信息
- `sessions` - 历史会话列表

### Getters (计算属性)
- `hasMessages` - 是否有消息
- `lastMessage` - 最后一条消息

### Methods
- `init()` - 初始化（加载历史或创建新会话）
- `sendMessage(content)` - 发送消息
- `loadSessions()` - 加载会话列表
- `loadSession(key)` - 加载指定会话
- `createNewSession()` - 创建新会话
- `saveSession()` - 保存当前会话到后端
- `deleteSession(key)` - 删除会话
- `formatMarkdown(content)` - 格式化 Markdown

## ChatPanel Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| messages | Array | [] | 消息列表 |
| isLoading | Boolean | false | 加载状态 |
| error | String | null | 错误信息 |
| sessions | Array | [] | 历史会话列表 |
| currentSessionKey | String | '' | 当前会话 key |
| showSidebar | Boolean | true | 是否显示侧边栏 |
| welcomeTitle | String | '开始对话' | 欢迎标题 |
| welcomeDescription | String | ... | 欢迎描述 |
| placeholder | String | '输入消息...' | 输入框占位符 |

## Events

- `@send(message)` - 用户发送消息
- `@new-chat` - 点击新建对话
- `@select-session(key)` - 选择历史会话
- `@delete-session(key)` - 删除会话

## 迁移指南

### 从旧架构迁移

1. **替换 API 调用**
   - 旧：`import { api } from '@/api/chat.js'`
   - 新：`import { chatApi } from '@/api/index.js'`

2. **替换状态管理**
   - 旧：使用 Pinia store
   - 新：`const chat = useChat('sidebar', '标题')`

3. **替换组件**
   - 旧：`<ChatContainer :sidebar="..." />`
   - 新：`<ChatPanel :messages="chat.messages.value" ... />`

4. **路由更新**
   - 在 router.js 中替换为新页面组件

## 后端要求

后端已支持新架构：
- GET `/api/chat/history?sidebar=xxx` - 按 sidebar 过滤
- POST `/api/chat/history` - 保存时包含 sidebar 字段
- 数据库已有 `sidebar` 列

## 优势

1. **清晰**：每个页面独立，不互相干扰
2. **简单**：不需要复杂的 store 管理
3. **可复用**：ChatPanel 组件可复用于所有页面
4. **可测试**：useChat 逻辑可单独测试
5. **可维护**：代码组织清晰，易于理解
