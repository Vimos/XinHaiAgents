<template>
  <ChatContainer
    sidebar="cpsycoun"
    title="📖 中文咨询"
    assistant-name="中文咨询师"
    icon="📖"
    welcome-title="CPsyCoun中文心理咨询"
    welcome-description="基于Memo2Demo的中文专业心理咨询系统，融合9大主题和7大治疗流派。"
    :quick-starters="[
      '我最近工作压力很大',
      '和家人关系不太好',
      '总是感到很焦虑怎么办',
      '我想学习情绪管理'
    ]"
    system-prompt="你是中文心理咨询师，基于CPsyCoun框架。你熟悉7大治疗流派（CBT、人本主义、精神分析、家庭治疗等），能够处理9大主题（情绪管理、人际关系、职业发展、亲子教育等）。你擅长使用Memo2Demo方法，从咨询报告重建高质量多轮对话。请用中文进行专业、温暖的心理咨询服务。"
  />
</template>

<script setup>
import ChatContainer from '@/components/ChatContainer.vue';
</script>
