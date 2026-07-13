import React, { useState, useEffect } from 'react';
import { Box, Text, useInput } from 'ink';
import { Command, filterCommands, COMMAND_CATEGORIES } from '../utils/commands';

interface CommandPaletteProps {
    commands: Command[];
    query: string;
    onSelect: (command: Command) => void;
    onClose: () => void;
}

const CommandPalette: React.FC<CommandPaletteProps> = ({ commands, query, onSelect, onClose }) => {
    const [selectedIndex, setSelectedIndex] = useState(0);
    const filteredCommands = filterCommands(commands, query);

    // 按分类分组
    const groupedCommands = COMMAND_CATEGORIES.map(category => ({
        ...category,
        commands: filteredCommands.filter(cmd => cmd.category === category.id)
    })).filter(group => group.commands.length > 0);

    // 扁平化命令列表
    const flatCommands = groupedCommands.flatMap(group => group.commands);

    useEffect(() => {
        setSelectedIndex(0);
    }, [query]);

    useInput((input, key) => {
        if (key.escape) {
            onClose();
            return;
        }

        if (key.return) {
            if (flatCommands[selectedIndex]) {
                onSelect(flatCommands[selectedIndex]);
            }
            return;
        }

        if (key.upArrow) {
            setSelectedIndex(prev => Math.max(0, prev - 1));
        }

        if (key.downArrow) {
            setSelectedIndex(prev => Math.min(flatCommands.length - 1, prev + 1));
        }
    });

    if (flatCommands.length === 0) {
        return (
            <Box flexDirection="column" borderStyle="round" borderColor="gray" paddingX={1}>
                <Text color="gray">没有匹配的命令</Text>
            </Box>
        );
    }

    let currentIndex = 0;

    return (
        <Box flexDirection="column" borderStyle="round" borderColor="cyan" paddingX={1}>
            <Text color="cyan" bold>命令面板</Text>
            <Text color="gray">{'─'.repeat(40)}</Text>
            
            {groupedCommands.map(group => (
                <Box key={group.id} flexDirection="column" marginBottom={1}>
                    <Text color="yellow" bold>{group.icon} {group.name}</Text>
                    {group.commands.map(cmd => {
                        const index = currentIndex++;
                        const isSelected = index === selectedIndex;
                        return (
                            <Box key={cmd.name} paddingLeft={2}>
                                <Text color={isSelected ? 'cyan' : 'white'}>
                                    {isSelected ? '▶ ' : '  '}
                                    {cmd.icon} /{cmd.name}
                                </Text>
                                <Text color="gray"> - {cmd.description}</Text>
                            </Box>
                        );
                    })}
                </Box>
            ))}
            
            <Text color="gray">{'─'.repeat(40)}</Text>
            <Text color="gray">↑↓ 选择 | Enter 确认 | Esc 关闭</Text>
        </Box>
    );
};

export default CommandPalette;
