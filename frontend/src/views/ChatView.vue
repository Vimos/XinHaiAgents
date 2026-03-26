<template>
  <ChatContainer
    sidebar="chat"
    title="💬 心理咨询"
    assistant-name="心海"
    icon="🌊"
    welcome-title="欢迎来到心海"
    welcome-description="我是您的AI心理咨询助手，可以为您提供情感支持和专业建议。"
    :quick-starters="[
      '我最近感到很焦虑',
      '如何改善睡眠质量？',
      '工作中压力很大怎么办？',
      '如何与他人更好地沟通？'
    ]"
    system-prompt="你是心海(XinHai)，一位专业的心理咨询助手。你具备丰富的心理学知识，包括CBT、情感支持、危机干预等专业技能。你的回复应该专业、有同理心、富有洞察力。"
  />
</template>

<script setup>
import ChatContainer from '@/components/ChatContainer.vue';
</script>
