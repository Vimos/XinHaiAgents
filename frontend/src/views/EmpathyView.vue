<template>
  <ChatContainer
    sidebar="empathy"
    title="❤️ 共情对话"
    assistant-name="共情助手"
    icon="❤️"
    welcome-title="APTNESS共情对话"
    welcome-description="基于评估理论和情感支持策略的共情回复生成系统。"
    :quick-starters="[
      '我感到非常难过',
      '没有人能理解我',
      '我不知道该怎么办',
      '你能理解我的感受吗？'
    ]"
    system-prompt="你是共情助手，基于APTNESS框架（CIKM 2024）。你需要：1）识别来访者的情绪状态（使用情感调色板的7大类别+23种细分情绪）；2）应用适当的情感支持策略（提供认可、情感验证、积极重塑等17种策略之一）；3）基于Emotion-Factor-Situation三维框架进行回应。请确保回复既专业又富有同理心。"
  />
</template>

<script setup>
import ChatContainer from '@/components/ChatContainer.vue';
</script>
