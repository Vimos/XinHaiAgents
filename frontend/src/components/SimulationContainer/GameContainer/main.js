import { Boot } from './scenes/Boot';
import { Game } from './scenes/Game';
import { GameOver } from './scenes/GameOver';
import { MainMenu } from './scenes/MainMenu';
import { MultiAgentScene } from './scenes/MultiAgentScene';
import Phaser from 'phaser';
import { Preloader } from './scenes/Preloader';

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
        MultiAgentScene,  // 使用新的多智能体场景
        Game,
        GameOver
    ],
    scale: {
        mode: Phaser.Scale.FIT,
        autoCenter: Phaser.Scale.CENTER_BOTH
    }
};

const StartGame = (parent) => {
    return new Phaser.Game({ ...config, parent });
}

export default StartGame;
