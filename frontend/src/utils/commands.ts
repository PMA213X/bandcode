// 命令定义

export interface Command {
    name: string;           // 命令名称
    shortcut?: string;      // 快捷键
    description: string;    // 描述
    icon: string;           // 图标
    action: () => void;     // 执行动作
    category: string;       // 分类
}

export const COMMAND_CATEGORIES = [
    { id: 'general', name: '通用', icon: '📋' },
    { id: 'settings', name: '设置', icon: '⚙️' },
    { id: 'memory', name: '记忆', icon: '🧠' },
    { id: 'agent', name: '智能体', icon: '🤖' },
    { id: 'tool', name: '工具', icon: '🔧' },
    { id: 'file', name: '文件', icon: '📄' },
];

export function createCommands(navigate: (view: string) => void): Command[] {
    return [
        // 通用命令
        {
            name: 'help',
            description: '显示帮助信息',
            icon: '❓',
            category: 'general',
            action: () => navigate('help'),
        },
        {
            name: 'clear',
            description: '清屏',
            icon: '🗑️',
            category: 'general',
            action: () => navigate('clear'),
        },
        {
            name: 'status',
            description: '显示系统状态',
            icon: '📊',
            category: 'general',
            action: () => navigate('status'),
        },
        
        // 设置命令
        {
            name: 'settings',
            description: '打开设置面板',
            icon: '⚙️',
            category: 'settings',
            action: () => navigate('settings'),
        },
        {
            name: 'settings model',
            description: '模型设置',
            icon: '🤖',
            category: 'settings',
            action: () => navigate('settings-model'),
        },
        {
            name: 'settings agent',
            description: 'Agent 设置',
            icon: '🤖',
            category: 'settings',
            action: () => navigate('settings-agent'),
        },
        {
            name: 'settings memory',
            description: 'Memory 设置',
            icon: '🧠',
            category: 'settings',
            action: () => navigate('settings-memory'),
        },
        {
            name: 'settings workflow',
            description: 'Workflow 设置',
            icon: '⚡',
            category: 'settings',
            action: () => navigate('settings-workflow'),
        },
        
        // 记忆命令
        {
            name: 'memory',
            description: '查看 Memory',
            icon: '🧠',
            category: 'memory',
            action: () => navigate('memory'),
        },
        {
            name: 'memory global',
            description: '查看全局 Memory',
            icon: '🌍',
            category: 'memory',
            action: () => navigate('memory-global'),
        },
        {
            name: 'memory project',
            description: '查看项目 Memory',
            icon: '📁',
            category: 'memory',
            action: () => navigate('memory-project'),
        },
        
        // Agent 命令
        {
            name: 'agents',
            description: '列出所有 Agent',
            icon: '🤖',
            category: 'agent',
            action: () => navigate('agents'),
        },
        
        // 工具命令
        {
            name: 'tools',
            description: '列出所有工具',
            icon: '🔧',
            category: 'tool',
            action: () => navigate('tools'),
        },
    ];
}

export function filterCommands(commands: Command[], query: string): Command[] {
    if (!query) return commands;
    const lowerQuery = query.toLowerCase();
    return commands.filter(cmd => 
        cmd.name.toLowerCase().includes(lowerQuery) ||
        cmd.description.toLowerCase().includes(lowerQuery)
    );
}
