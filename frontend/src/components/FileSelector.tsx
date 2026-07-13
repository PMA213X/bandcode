import React, { useState, useEffect } from 'react';
import { Box, Text, useInput } from 'ink';

interface FileItem {
    name: string;
    path: string;
    isDirectory: boolean;
}

interface FileSelectorProps {
    query: string;
    onSelect: (file: FileItem) => void;
    onClose: () => void;
}

const FileSelector: React.FC<FileSelectorProps> = ({ query, onSelect, onClose }) => {
    const [files, setFiles] = useState<FileItem[]>([]);
    const [selectedIndex, setSelectedIndex] = useState(0);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // TODO: 从后端获取文件列表
        // 临时使用模拟数据
        const mockFiles: FileItem[] = [
            { name: 'main.py', path: 'backend/main.py', isDirectory: false },
            { name: 'README.md', path: 'README.md', isDirectory: false },
            { name: 'backend/', path: 'backend/', isDirectory: true },
            { name: 'frontend/', path: 'frontend/', isDirectory: true },
            { name: 'docs/', path: 'docs/', isDirectory: true },
        ];
        
        const filtered = query
            ? mockFiles.filter(f => f.name.toLowerCase().includes(query.toLowerCase()))
            : mockFiles;
        
        setFiles(filtered);
        setLoading(false);
    }, [query]);

    useInput((input, key) => {
        if (key.escape) {
            onClose();
            return;
        }

        if (key.return && files[selectedIndex]) {
            onSelect(files[selectedIndex]);
            return;
        }

        if (key.upArrow) {
            setSelectedIndex(prev => Math.max(0, prev - 1));
        }

        if (key.downArrow) {
            setSelectedIndex(prev => Math.min(files.length - 1, prev + 1));
        }
    });

    if (loading) {
        return (
            <Box borderStyle="round" borderColor="gray" paddingX={1}>
                <Text color="gray">加载中...</Text>
            </Box>
        );
    }

    if (files.length === 0) {
        return (
            <Box borderStyle="round" borderColor="gray" paddingX={1}>
                <Text color="gray">没有找到文件</Text>
            </Box>
        );
    }

    return (
        <Box flexDirection="column" borderStyle="round" borderColor="yellow" paddingX={1}>
            <Text color="yellow" bold>文件选择</Text>
            <Text color="gray">{'─'.repeat(40)}</Text>
            
            {files.map((file, index) => (
                <Box key={file.path}>
                    <Text color={index === selectedIndex ? 'cyan' : 'white'}>
                        {index === selectedIndex ? '▶ ' : '  '}
                        {file.isDirectory ? '📁' : '📄'} {file.name}
                    </Text>
                </Box>
            ))}
            
            <Text color="gray">{'─'.repeat(40)}</Text>
            <Text color="gray">↑↓ 选择 | Enter 确认 | Esc 关闭</Text>
        </Box>
    );
};

export default FileSelector;
