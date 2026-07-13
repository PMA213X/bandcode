import React, { useState } from 'react';
import { Box, Text, useInput } from 'ink';
import { MODEL_PROVIDERS, ModelProvider, Model } from '../utils/modelProviders';

interface ModelSelectorProps {
    onSelectProvider: (provider: ModelProvider) => void;
    onSelectModel: (model: Model) => void;
    onClose: () => void;
    selectedProviderId?: string;
    selectedModelId?: string;
}

const ModelSelector: React.FC<ModelSelectorProps> = ({
    onSelectProvider,
    onSelectModel,
    onClose,
    selectedProviderId,
    selectedModelId,
}) => {
    const [mode, setMode] = useState<'provider' | 'model'>('provider');
    const [selectedProviderIndex, setSelectedProviderIndex] = useState(0);
    const [selectedModelIndex, setSelectedModelIndex] = useState(0);

    const currentProvider = MODEL_PROVIDERS[selectedProviderIndex];

    useInput((input, key) => {
        if (key.escape) {
            if (mode === 'model') {
                setMode('provider');
            } else {
                onClose();
            }
            return;
        }

        if (mode === 'provider') {
            if (key.upArrow) {
                setSelectedProviderIndex(prev => Math.max(0, prev - 1));
            }
            if (key.downArrow) {
                setSelectedProviderIndex(prev => Math.min(MODEL_PROVIDERS.length - 1, prev + 1));
            }
            if (key.return) {
                onSelectProvider(currentProvider);
                if (currentProvider.models.length > 0) {
                    setMode('model');
                    setSelectedModelIndex(0);
                }
            }
        } else {
            if (key.upArrow) {
                setSelectedModelIndex(prev => Math.max(0, prev - 1));
            }
            if (key.downArrow) {
                setSelectedModelIndex(prev => Math.min(currentProvider.models.length - 1, prev + 1));
            }
            if (key.return && currentProvider.models[selectedModelIndex]) {
                onSelectModel(currentProvider.models[selectedModelIndex]);
                onClose();
            }
        }
    });

    return (
        <Box flexDirection="column" borderStyle="round" borderColor="cyan" paddingX={1}>
            {mode === 'provider' ? (
                <>
                    <Text color="cyan" bold>选择模型提供商</Text>
                    <Text color="gray">{'─'.repeat(40)}</Text>
                    {MODEL_PROVIDERS.map((provider, index) => (
                        <Box key={provider.id}>
                            <Text color={index === selectedProviderIndex ? 'cyan' : 'white'}>
                                {index === selectedProviderIndex ? '▶ ' : '  '}
                                {provider.icon} {provider.name}
                            </Text>
                        </Box>
                    ))}
                    <Text color="gray">{'─'.repeat(40)}</Text>
                    <Text color="gray">↑↓ 选择 | Enter 确认 | Esc 关闭</Text>
                </>
            ) : (
                <>
                    <Text color="cyan" bold>{currentProvider.icon} {currentProvider.name} - 选择模型</Text>
                    <Text color="gray">{'─'.repeat(40)}</Text>
                    {currentProvider.models.map((model, index) => (
                        <Box key={model.id} flexDirection="column">
                            <Text color={index === selectedModelIndex ? 'cyan' : 'white'}>
                                {index === selectedModelIndex ? '▶ ' : '  '}
                                {model.name}
                            </Text>
                            <Text color="gray">    {model.description}</Text>
                        </Box>
                    ))}
                    <Text color="gray">{'─'.repeat(40)}</Text>
                    <Text color="gray">↑↓ 选择 | Enter 确认 | Esc 返回</Text>
                </>
            )}
        </Box>
    );
};

export default ModelSelector;
