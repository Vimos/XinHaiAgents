<template>
  <ChatContainer
    sidebar="cbt"
    title="🧠 CBT 治疗"
    assistant-name="CBT 咨询师"
    icon="🧠"
    welcome-title="CBT 认知行为治疗"
    welcome-description="通过对话进行认知行为疗法，帮助你识别和改变负面思维模式。"
    :quick-starters="[
      '我最近总是感到焦虑',
      '我想改变我的负面想法',
      '帮我分析这个情境',
      '教我一些放松技巧'
    ]"
    system-prompt="你是 CBT 认知行为治疗师。你擅长使用认知行为疗法技术，帮助来访者识别负面自动思维、挑战不合理信念、建立更健康的认知模式。你会用温暖、专业的态度进行对话。"
  />
</template>

<script setup>
import ChatContainer from '@/components/ChatContainer.vue';
</script>
