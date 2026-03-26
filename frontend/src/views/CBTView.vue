<template>
  <ChatContainer
    sidebar="cbt"
    title="🧠 CBT治疗"
    assistant-name="CBT治疗师"
    icon="🎯"
    welcome-title="CBT认知行为治疗"
    welcome-description="基于认知行为疗法的专业咨询，帮助识别和改变负面思维模式。"
    :quick-starters="[
      '我总是想太多，控制不了',
      '我觉得自己什么都做不好',
      '为什么我总是这么焦虑？',
      '如何挑战我的负面想法？'
    ]"
    system-prompt="你是CBT治疗师，专注于认知行为疗法。你会帮助来访者识别认知扭曲、挑战负面思维、建立更健康的思维模式。请使用苏格拉底式提问引导来访者自我发现。"
  />
</template>

<script setup>
import ChatContainer from '@/components/ChatContainer.vue';
</script>
