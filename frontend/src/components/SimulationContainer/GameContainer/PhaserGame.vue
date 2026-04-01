<script setup>
import { onMounted, onUnmounted, ref } from 'vue';
import { EventBus } from './EventBus';
import StartGame from './main';

// Save the current scene instance
const scene = ref();
const game = ref();

const emit = defineEmits(['current-active-scene']);

onMounted(() => {
    console.log('[PhaserGame] Starting game...');
    
    game.value = StartGame('game-container');

    EventBus.on('current-scene-ready', (currentScene) => {
        console.log('[PhaserGame] Scene ready:', currentScene.scene?.key);
        emit('current-active-scene', currentScene);
        scene.value = currentScene;
    });
});

onUnmounted(() => {
    if (game.value) {
        game.value.destroy(true);
        game.value = null;
    }
});

defineExpose({ scene, game });
</script>

<template>
    <div id="game-container" class="game-container"></div>
</template>

<style scoped>
.game-container {
    width: 100%;
    height: 100%;
    min-height: 600px;
    background: #0A1628;
    border-radius: 12px;
    overflow: hidden;
}

.game-container :deep(canvas) {
    display: block;
    /* 让 Phaser 自己控制尺寸以保持宽高比 */
}
</style>
