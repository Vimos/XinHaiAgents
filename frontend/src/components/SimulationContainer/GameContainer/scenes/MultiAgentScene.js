import Phaser from 'phaser';

/**
 * 简化版多智能体场景
 * - 静态场景：咨询室
 * - Agent 固定位置
 * - 对话气泡显示
 * - 点击交互
 */

export class MultiAgentScene extends Phaser.Scene {
    constructor() {
        super({ key: 'MultiAgentScene' });
        this.agents = new Map();
        this.messages = [];
    }

    preload() {
        // 创建简单的精灵纹理
        this.load.setBaseURL('');
    }

    create() {
        console.log('[MultiAgentScene] Creating scene...');
        
        // 海洋主题背景
        this.createBackground();
        
        // 创建房间布局
        this.createRoomLayout();
        
        // 创建示例 Agent
        this.createAgents();
        
        // 创建 UI 层
        this.createUI();
        
        // 监听来自 Vue 的事件
        this.setupEventListeners();
        
        // 模拟对话流
        this.startSimulation();
        
        console.log('[MultiAgentScene] Scene created successfully');
        
        // 通知场景已准备好
        if (this.game && this.game.events) {
            this.game.events.emit('current-scene-ready', this);
        }
    }

    setupEventListeners() {
        // 监听 agent-speech 事件（来自 Vue 组件）
        this.events.on('agent-speech', (data) => {
            console.log('[MultiAgentScene] Received agent-speech:', data);
            
            // 将 agentId 映射到场景中的 agent
            const agentId = this.mapAgentId(data.agentId, data.agentName);
            if (agentId) {
                this.showMessage(agentId, data.content);
            }
        });
    }

    mapAgentId(agentId, agentName) {
        // 尝试直接匹配 ID
        if (this.agents.has(String(agentId))) {
            return String(agentId);
        }
        
        // 根据名字映射到场景中的 agent
        const nameToId = {
            '用户': 'patient',
            '来访者': 'patient',
            '咨询者': 'patient',
            '助手': 'therapist',
            '咨询师': 'therapist',
            '治疗师': 'therapist',
            '督导': 'supervisor',
            '督导师': 'supervisor'
        };
        
        const mappedId = nameToId[agentName];
        if (mappedId && this.agents.has(mappedId)) {
            return mappedId;
        }
        
        // 默认返回第一个 agent
        return this.agents.keys().next().value;
    }

    createBackground() {
        // 深海渐变背景
        const graphics = this.add.graphics();
        
        // 上深下浅的海洋渐变
        for (let y = 0; y < 768; y++) {
            const ratio = y / 768;
            const r = Math.floor(10 + ratio * 20);
            const g = Math.floor(22 + ratio * 40);
            const b = Math.floor(40 + ratio * 55);
            graphics.fillStyle(Phaser.Display.Color.GetColor(r, g, b), 1);
            graphics.fillRect(0, y, 1024, 1);
        }
        
        // 添加波浪装饰
        this.createWaves();
    }

    createWaves() {
        // 创建波浪纹理
        const waveGraphics = this.make.graphics({ x: 0, y: 0, add: false });
        waveGraphics.fillStyle(0x00D4FF, 0.1);
        waveGraphics.fillCircle(100, 50, 80);
        waveGraphics.fillCircle(200, 50, 60);
        waveGraphics.fillCircle(300, 50, 70);
        waveGraphics.generateTexture('wave', 400, 100);
        
        // 添加多个波浪层
        for (let i = 0; i < 3; i++) {
            const wave = this.add.image(512, 700 + i * 30, 'wave');
            wave.setAlpha(0.1 - i * 0.02);
            wave.setScale(3);
            
            // 波浪动画
            this.tweens.add({
                targets: wave,
                x: 600,
                duration: 3000 + i * 500,
                yoyo: true,
                repeat: -1,
                ease: 'Sine.easeInOut'
            });
        }
    }

    createRoomLayout() {
        const graphics = this.add.graphics();
        
        // 房间区域 - 玻璃拟态风格
        const roomX = 100;
        const roomY = 100;
        const roomW = 824;
        const roomH = 568;
        
        // 房间背景
        graphics.fillStyle(0x1E3A5F, 0.8);
        graphics.fillRoundedRect(roomX, roomY, roomW, roomH, 20);
        
        // 边框发光
        graphics.lineStyle(2, 0x00D4FF, 0.5);
        graphics.strokeRoundedRect(roomX, roomY, roomW, roomH, 20);
        
        // 房间标题
        this.add.text(roomX + 20, roomY + 20, '🏥 心理咨询室', {
            fontSize: '24px',
            fontFamily: 'Noto Sans SC',
            color: '#00D4FF',
            fontStyle: 'bold'
        });
        
        // 家具 - 沙发区域
        this.createFurniture(200, 350, '🛋️', '咨询沙发');
        this.createFurniture(500, 250, '🪑', '咨询师座椅');
        this.createFurniture(750, 400, '🌿', '绿植区');
        this.createFurniture(150, 550, '📚', '书架');
        this.createFurniture(800, 550, '☕', '休息角');
    }

    createFurniture(x, y, emoji, label) {
        const container = this.add.container(x, y);
        
        // 家具背景
        const bg = this.add.graphics();
        bg.fillStyle(0x0A1628, 0.6);
        bg.fillRoundedRect(-40, -40, 80, 80, 10);
        bg.lineStyle(1, 0x00D4FF, 0.3);
        bg.strokeRoundedRect(-40, -40, 80, 80, 10);
        container.add(bg);
        
        // 家具图标
        const icon = this.add.text(0, -5, emoji, {
            fontSize: '32px'
        }).setOrigin(0.5);
        container.add(icon);
        
        // 标签
        const text = this.add.text(0, 25, label, {
            fontSize: '12px',
            fontFamily: 'Noto Sans SC',
            color: '#94A3B8'
        }).setOrigin(0.5);
        container.add(text);
    }

    createAgents() {
        // 创建咨询师 Agent
        this.createAgent({
            id: 'therapist',
            name: '咨询师',
            role: 'CBT治疗师',
            avatar: '🧑‍⚕️',
            x: 500,
            y: 350,
            color: 0x00D4FF
        });
        
        // 创建来访者 Agent
        this.createAgent({
            id: 'patient',
            name: '来访者',
            role: '焦虑患者',
            avatar: '😔',
            x: 250,
            y: 380,
            color: 0x9F7AEA
        });
        
        // 创建观察者 Agent（督导）
        this.createAgent({
            id: 'supervisor',
            name: '督导',
            role: '督导专家',
            avatar: '👁️',
            x: 750,
            y: 200,
            color: 0x38B2AC
        });
    }

    createAgent(config) {
        const container = this.add.container(config.x, config.y);
        container.setSize(80, 100);
        container.setInteractive({ useHandCursor: true });
        
        // Agent 背景光圈
        const glow = this.add.graphics();
        glow.fillStyle(config.color, 0.2);
        glow.fillCircle(0, 20, 45);
        container.add(glow);
        
        // 呼吸动画
        this.tweens.add({
            targets: glow,
            scale: 1.1,
            alpha: 0.3,
            duration: 2000,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });
        
        // Agent 头像
        const avatar = this.add.text(0, 0, config.avatar, {
            fontSize: '48px'
        }).setOrigin(0.5);
        container.add(avatar);
        
        // 名字标签
        const nameTag = this.add.text(0, 35, config.name, {
            fontSize: '14px',
            fontFamily: 'Noto Sans SC',
            color: '#F0F9FF',
            fontStyle: 'bold',
            backgroundColor: '#1E3A5F',
            padding: { x: 8, y: 2 }
        }).setOrigin(0.5);
        container.add(nameTag);
        
        // 角色标签
        const roleTag = this.add.text(0, 55, config.role, {
            fontSize: '11px',
            fontFamily: 'Noto Sans SC',
            color: '#94A3B8'
        }).setOrigin(0.5);
        container.add(roleTag);
        
        // 状态指示器
        const statusDot = this.add.graphics();
        statusDot.fillStyle(0x38B2AC, 1);
        statusDot.fillCircle(25, -15, 6);
        container.add(statusDot);
        
        // 状态脉冲动画
        this.tweens.add({
            targets: statusDot,
            scale: 1.5,
            alpha: 0.5,
            duration: 1000,
            yoyo: true,
            repeat: -1
        });
        
        // 点击事件
        container.on('pointerdown', () => {
            this.selectAgent(config);
        });
        
        // 悬停效果
        container.on('pointerover', () => {
            this.tweens.add({
                targets: container,
                scale: 1.1,
                duration: 200
            });
        });
        
        container.on('pointerout', () => {
            this.tweens.add({
                targets: container,
                scale: 1,
                duration: 200
            });
        });
        
        // 存储 Agent 引用
        this.agents.set(config.id, {
            config,
            container,
            avatar,
            messages: []
        });
        
        return container;
    }

    createUI() {
        // 控制面板
        const panelX = 20;
        const panelY = 20;
        
        const panel = this.add.graphics();
        panel.fillStyle(0x0A1628, 0.9);
        panel.fillRoundedRect(panelX, panelY, 200, 150, 10);
        panel.lineStyle(1, 0x00D4FF, 0.3);
        panel.strokeRoundedRect(panelX, panelY, 200, 150, 10);
        
        // 面板标题
        this.add.text(panelX + 15, panelY + 15, '控制面板', {
            fontSize: '16px',
            fontFamily: 'Noto Sans SC',
            color: '#00D4FF',
            fontStyle: 'bold'
        });
        
        // 创建按钮
        this.createButton(panelX + 100, panelY + 60, '▶️ 开始对话', () => {
            this.startDialogue();
        });
        
        this.createButton(panelX + 100, panelY + 110, '🔄 重置场景', () => {
            this.resetScene();
        });
        
        // Agent 信息面板（右侧）
        this.infoPanel = this.createInfoPanel();
    }

    createButton(x, y, text, callback) {
        const container = this.add.container(x, y);
        container.setSize(160, 36);
        container.setInteractive({ useHandCursor: true });
        
        const bg = this.add.graphics();
        bg.fillStyle(0x1E3A5F, 1);
        bg.fillRoundedRect(-80, -18, 160, 36, 8);
        bg.lineStyle(1, 0x00D4FF, 0.5);
        bg.strokeRoundedRect(-80, -18, 160, 36, 8);
        container.add(bg);
        
        const label = this.add.text(0, 0, text, {
            fontSize: '14px',
            fontFamily: 'Noto Sans SC',
            color: '#F0F9FF'
        }).setOrigin(0.5);
        container.add(label);
        
        container.on('pointerdown', callback);
        
        container.on('pointerover', () => {
            bg.clear();
            bg.fillStyle(0x00D4FF, 0.2);
            bg.fillRoundedRect(-80, -18, 160, 36, 8);
            bg.lineStyle(1, 0x00D4FF, 1);
            bg.strokeRoundedRect(-80, -18, 160, 36, 8);
        });
        
        container.on('pointerout', () => {
            bg.clear();
            bg.fillStyle(0x1E3A5F, 1);
            bg.fillRoundedRect(-80, -18, 160, 36, 8);
            bg.lineStyle(1, 0x00D4FF, 0.5);
            bg.strokeRoundedRect(-80, -18, 160, 36, 8);
        });
        
        return container;
    }

    createInfoPanel() {
        const panelX = 750;
        const panelY = 120;
        
        const container = this.add.container(panelX, panelY);
        container.setVisible(false);
        
        const bg = this.add.graphics();
        bg.fillStyle(0x0A1628, 0.95);
        bg.fillRoundedRect(0, 0, 240, 200, 10);
        bg.lineStyle(2, 0x00D4FF, 0.5);
        bg.strokeRoundedRect(0, 0, 240, 200, 10);
        container.add(bg);
        
        const title = this.add.text(15, 15, 'Agent 信息', {
            fontSize: '18px',
            fontFamily: 'Noto Sans SC',
            color: '#00D4FF',
            fontStyle: 'bold'
        });
        container.add(title);
        
        const content = this.add.text(15, 50, '', {
            fontSize: '14px',
            fontFamily: 'Noto Sans SC',
            color: '#F0F9FF',
            lineSpacing: 8
        });
        container.add(content);
        
        return { container, content };
    }

    selectAgent(config) {
        this.infoPanel.container.setVisible(true);
        this.infoPanel.content.setText([
            `名称: ${config.name}`,
            `角色: ${config.role}`,
            `状态: 在线`,
            `对话数: ${Math.floor(Math.random() * 10)}`,
            '',
            '💡 点击开始对话'
        ].join('\n'));
    }

    showMessage(agentId, message) {
        const agent = this.agents.get(agentId);
        if (!agent) return;
        
        const { container } = agent;
        
        // 创建对话气泡
        const bubbleY = -70;
        
        const bubbleBg = this.add.graphics();
        const padding = 10;
        const maxWidth = 200;
        
        // 计算文字尺寸
        const textObj = this.add.text(0, 0, message, {
            fontSize: '13px',
            fontFamily: 'Noto Sans SC',
            color: '#0A1628',
            wordWrap: { width: maxWidth - padding * 2 }
        });
        const bounds = textObj.getBounds();
        
        // 绘制气泡背景
        const bubbleWidth = Math.min(bounds.width + padding * 2, maxWidth);
        const bubbleHeight = bounds.height + padding * 2;
        
        bubbleBg.fillStyle(0xF0F9FF, 0.95);
        bubbleBg.fillRoundedRect(-bubbleWidth/2, bubbleY - bubbleHeight, bubbleWidth, bubbleHeight, 8);
        
        // 小三角
        bubbleBg.fillTriangle(
            -8, bubbleY,
            8, bubbleY,
            0, bubbleY + 8
        );
        
        container.add(bubbleBg);
        
        // 添加文字
        textObj.setPosition(-bubbleWidth/2 + padding, bubbleY - bubbleHeight + padding);
        container.add(textObj);
        
        // 3秒后消失
        this.time.delayedCall(3000, () => {
            bubbleBg.destroy();
            textObj.destroy();
        });
    }

    startDialogue() {
        // 模拟对话流程
        const dialogues = [
            { agent: 'patient', text: '我最近总是感到很焦虑...' },
            { agent: 'therapist', text: '能具体说说是什么让你感到焦虑吗？' },
            { agent: 'patient', text: '工作压力很大，晚上睡不着。' },
            { agent: 'supervisor', text: '[督导] 注意识别认知扭曲' },
            { agent: 'therapist', text: '听起来你有很多担忧，我们一起梳理一下。' }
        ];
        
        let index = 0;
        const showNext = () => {
            if (index >= dialogues.length) return;
            
            const { agent, text } = dialogues[index];
            this.showMessage(agent, text);
            index++;
            
            this.time.delayedCall(2500, showNext);
        };
        
        showNext();
    }

    startSimulation() {
        // 场景初始化完成提示
        this.add.text(512, 720, '点击 Agent 查看详情 | 点击"开始对话"模拟咨询流程', {
            fontSize: '14px',
            fontFamily: 'Noto Sans SC',
            color: '#94A3B8'
        }).setOrigin(0.5);
    }

    resetScene() {
        // 清除所有对话气泡
        this.children.list
            .filter(child => child.type === 'Container')
            .forEach(container => {
                // 保留 Agent 容器，移除气泡
                const toRemove = container.list.filter(child => 
                    child !== container.list[0] && // 保留 glow
                    child !== container.list[1] && // 保留 avatar
                    child !== container.list[2] && // 保留 nameTag
                    child !== container.list[3] && // 保留 roleTag
                    child !== container.list[4]    // 保留 statusDot
                );
                toRemove.forEach(child => child.destroy());
            });
        
        this.infoPanel.container.setVisible(false);
    }

    update() {
        // 可以在这里添加实时更新逻辑
    }
}
