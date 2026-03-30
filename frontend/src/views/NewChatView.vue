<template>
  <ChatContainer
    sidebar="chat"
    title="💬 AI 对话"
    assistant-name="AI 助手"
    icon="🤖"
    welcome-title="AI 对话助手"
    welcome-description="我是你的 AI 助手，可以回答问题、协助创作、分析数据等。"
    :quick-starters="[
      '帮我写一段 Python 代码',
      '解释一下量子力学',
      '给我讲个笑话',
      '推荐几本好书'
    ]"
    system-prompt="你是 AI 助手，能够回答各类问题、协助编程、解释概念、提供建议等。"
  />
</template>

<script setup>
import ChatContainer from '@/components/ChatContainer.vue';
</script>
