import { useState, useCallback } from 'react';
import { Command, createCommands } from '../utils/commands';

export function useCommands(navigate: (view: string) => void) {
    const [showCommandPalette, setShowCommandPalette] = useState(false);
    const [commandQuery, setCommandQuery] = useState('');
    const [showFileSelector, setShowFileSelector] = useState(false);
    const [fileQuery, setFileQuery] = useState('');

    const commands = createCommands(navigate);

    const handleInputChange = useCallback((value: string) => {
        // 检测 / 开头
        if (value.startsWith('/')) {
            setShowCommandPalette(true);
            setCommandQuery(value.slice(1));
            setShowFileSelector(false);
            return;
        }

        // 检测 @ 开头
        if (value.startsWith('@')) {
            setShowFileSelector(true);
            setFileQuery(value.slice(1));
            setShowCommandPalette(false);
            return;
        }

        // 都不是，关闭面板
        setShowCommandPalette(false);
        setShowFileSelector(false);
    }, []);

    const handleCommandSelect = useCallback((command: Command) => {
        setShowCommandPalette(false);
        setCommandQuery('');
        command.action();
    }, []);

    const handleFileSelect = useCallback((file: { name: string; path: string }) => {
        setShowFileSelector(false);
        setFileQuery('');
        // TODO: 插入文件路径到输入框
        return file.path;
    }, []);

    const closeCommandPalette = useCallback(() => {
        setShowCommandPalette(false);
        setCommandQuery('');
    }, []);

    const closeFileSelector = useCallback(() => {
        setShowFileSelector(false);
        setFileQuery('');
    }, []);

    return {
        showCommandPalette,
        commandQuery,
        showFileSelector,
        fileQuery,
        commands,
        handleInputChange,
        handleCommandSelect,
        handleFileSelect,
        closeCommandPalette,
        closeFileSelector,
    };
}
