// 模型提供商配置

export interface ModelProvider {
    id: string;
    name: string;
    icon: string;
    baseUrl: string;
    models: Model[];
}

export interface Model {
    id: string;
    name: string;
    description: string;
}

export const MODEL_PROVIDERS: ModelProvider[] = [
    {
        id: 'mimo',
        name: 'MiMo',
        icon: '🤖',
        baseUrl: 'https://api.mimo.example.com/v1',
        models: [
            { id: 'mimo-v2.5-pro', name: 'MiMo v2.5 Pro', description: '高难度任务' },
            { id: 'mimo-v2.5', name: 'MiMo v2.5', description: '低难度任务' },
        ]
    },
    {
        id: 'openai',
        name: 'OpenAI',
        icon: '🟢',
        baseUrl: 'https://api.openai.com/v1',
        models: [
            { id: 'gpt-4o', name: 'GPT-4o', description: '最新多模态模型' },
            { id: 'gpt-4o-mini', name: 'GPT-4o Mini', description: '轻量版' },
            { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', description: '经济实惠' },
        ]
    },
    {
        id: 'deepseek',
        name: 'DeepSeek',
        icon: '🔵',
        baseUrl: 'https://api.deepseek.com/v1',
        models: [
            { id: 'deepseek-chat', name: 'DeepSeek Chat', description: '通用对话' },
            { id: 'deepseek-coder', name: 'DeepSeek Coder', description: '代码生成' },
        ]
    },
    {
        id: 'claude',
        name: 'Claude',
        icon: '🟠',
        baseUrl: 'https://api.anthropic.com/v1',
        models: [
            { id: 'claude-3-opus', name: 'Claude 3 Opus', description: '最强能力' },
            { id: 'claude-3-sonnet', name: 'Claude 3 Sonnet', description: '平衡性能' },
        ]
    },
    {
        id: 'qwen',
        name: 'Qwen',
        icon: '🟣',
        baseUrl: 'https://dashscope.aliyuncs.com/api/v1',
        models: [
            { id: 'qwen-max', name: 'Qwen Max', description: '最强能力' },
            { id: 'qwen-plus', name: 'Qwen Plus', description: '平衡性能' },
            { id: 'qwen-turbo', name: 'Qwen Turbo', description: '快速响应' },
        ]
    },
    {
        id: 'custom',
        name: '自定义',
        icon: '⚙️',
        baseUrl: '',
        models: []
    }
];

export function getProviderById(id: string): ModelProvider | undefined {
    return MODEL_PROVIDERS.find(p => p.id === id);
}

export function getModelsByProviderId(providerId: string): Model[] {
    const provider = getProviderById(providerId);
    return provider ? provider.models : [];
}
