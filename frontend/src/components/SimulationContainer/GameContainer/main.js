import { Boot } from './scenes/Boot';
import { Game } from './scenes/Game';
import { GameOver } from './scenes/GameOver';
import { MainMenu } from './scenes/MainMenu';
import { MultiAgentScene } from './scenes/MultiAgentScene';
import Phaser from 'phaser';
import { Preloader } from './scenes/Preloader';

// 场景启动插件 - 跳过菜单直接启动 MultiAgentScene
class AutoStartPlugin extends Phaser.Plugins.BasePlugin {
    constructor(pluginManager) {
        super(pluginManager);
    }

    start() {
        this.game.events.on('ready', () => {
            console.log('[Phaser] Auto-starting MultiAgentScene...');
            // 延迟一点确保预加载完成
            setTimeout(() => {
                this.game.scene.start('MultiAgentScene');
            }, 100);
        });
    }
}

// 多智能体场景配置
const config = {
    type: Phaser.AUTO,
    width: 1024,
    height: 768,
    parent: 'game-container',
    backgroundColor: '#0A1628',
    scene: [
        Boot,
        Preloader,
        MainMenu,
        MultiAgentScene,
        Game,
        GameOver
    ],
    plugins: {
        global: [
            { key: 'AutoStartPlugin', plugin: AutoStartPlugin, start: true }
        ]
    },
    scale: {
        mode: Phaser.Scale.SHOW_ALL,
        autoCenter: Phaser.Scale.CENTER_BOTH
    }
};

const StartGame = (parent) => {
    return new Phaser.Game({ ...config, parent });
}

export default StartGame;
