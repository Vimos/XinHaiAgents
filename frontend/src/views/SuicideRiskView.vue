<template>
  <ChatContainer
    sidebar="suicide-risk"
    title="⚠️ 风险评估"
    assistant-name="风险评估专家"
    icon="⚠️"
    welcome-title="自杀风险评估"
    welcome-description="基于CLPsych 2024研究成果的专业自杀风险评估工具，提供6维度综合评估。"
    :quick-starters="[
      '评估当前风险等级',
      '解释6维度评估方法',
      '如何识别自杀信号？',
      '提供危机干预资源'
    ]"
    system-prompt="你是自杀风险评估专家。基于CLPsych 2024的研究成果，你需要从6个维度（自杀意念、计划、手段、时间、意图、预防因素）评估来访者的风险等级，并提供分级证据支持。请保持专业、谨慎、富有同理心。如果检测到高风险，请立即建议寻求专业帮助。"
  />
</template>

<script setup>
import ChatContainer from '@/components/ChatContainer.vue';
</script>
