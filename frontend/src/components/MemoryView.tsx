import React, { useEffect } from 'react';
import { Box, Text, useInput } from 'ink';
import { useMemory, MemoryLayer } from '../hooks/useMemory';

const LAYERS: { id: MemoryLayer; name: string; icon: string }[] = [
    { id: 'global', name: '全局', icon: '🌍' },
    { id: 'project', name: '项目', icon: '📁' },
    { id: 'task', name: '任务', icon: '📋' },
    { id: 'session', name: '会话', icon: '💬' },
    { id: 'checkpoint', name: '快照', icon: '📸' },
];

interface MemoryViewProps {
    onClose: () => void;
}

const MemoryView: React.FC<MemoryViewProps> = ({ onClose }) => {
    const {
        activeLayer,
        loading,
        error,
        switchLayer,
        refresh,
        currentContent,
        currentUpdatedAt,
    } = useMemory();

    useEffect(() => {
        switchLayer('global');
    }, []);

    useInput((input, key) => {
        if (key.escape || input === 'q') {
            onClose();
            return;
        }

        if (input === 'r') {
            refresh();
            return;
        }

        // 数字键切换层级
        const num = parseInt(input);
        if (num >= 1 && num <= LAYERS.length) {
            switchLayer(LAYERS[num - 1].id);
        }
    });

    return (
        <Box flexDirection="column" padding={1}>
            <Box marginBottom={1}>
                <Text color="cyan" bold>🧠 Memory 浏览器</Text>
            </Box>
            
            <Box marginBottom={1}>
                <Text color="gray">{'─'.repeat(60)}</Text>
            </Box>
            
            {/* 标签页 */}
            <Box marginBottom={1}>
                {LAYERS.map((layer, index) => (
                    <Box key={layer.id} marginRight={2}>
                        <Text 
                            color={activeLayer === layer.id ? 'cyan' : 'gray'}
                            bold={activeLayer === layer.id}
                        >
                            {activeLayer === layer.id ? '▶ ' : '  '}
                            {layer.icon} {layer.name} [{index + 1}]
                        </Text>
                    </Box>
                ))}
            </Box>
            
            <Box marginBottom={1}>
                <Text color="gray">{'─'.repeat(60)}</Text>
            </Box>
            
            {/* 内容区 */}
            <Box flexDirection="column" flexGrow={1} borderStyle="round" borderColor="gray" paddingX={1} paddingY={1}>
                {loading ? (
                    <Text color="yellow">加载中...</Text>
                ) : error ? (
                    <Text color="red">❌ {error}</Text>
                ) : currentContent ? (
                    <Box flexDirection="column">
                        <Text>{currentContent}</Text>
                    </Box>
                ) : (
                    <Text color="gray">暂无内容</Text>
                )}
            </Box>
            
            {/* 状态栏 */}
            <Box marginTop={1}>
                <Text color="gray">
                    {currentUpdatedAt && `更新时间: ${currentUpdatedAt}`}
                </Text>
            </Box>
            
            <Box marginTop={1}>
                <Text color="gray">{'─'.repeat(60)}</Text>
            </Box>
            
            <Box>
                <Text color="gray">
                    [1-5] 切换层级 | [r] 刷新 | [q/Esc] 返回
                </Text>
            </Box>
        </Box>
    );
};

export default MemoryView;
