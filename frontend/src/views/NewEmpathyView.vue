<template>
  <ChatContainer
    sidebar="empathy"
    title="💙 共情对话"
    assistant-name="共情伙伴"
    icon="💙"
    welcome-title="共情对话"
    welcome-description="一个倾听和理解的温暖空间，你可以安全地表达任何感受。"
    :quick-starters="[
      '我今天心情不太好',
      '想找人聊聊',
      '我感觉很孤独',
      '最近压力很大'
    ]"
    system-prompt="你是共情伙伴，专注于情感支持和倾听。你用温暖、接纳的态度回应，注重理解对方的感受，提供情感上的支持而非建议。你善于反映情绪、确认感受，让对方感到被理解和接纳。"
  />
</template>

<script setup>
import ChatContainer from '@/components/ChatContainer.vue';
</script>
