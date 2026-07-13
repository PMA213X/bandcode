import React, { useState } from 'react';
import { Box, Text, useInput, useApp } from 'ink';
import Chat from './components/Chat';
import Settings from './components/Settings';
import MemoryView from './components/MemoryView';
import Layout from './components/Layout';

type View = 'chat' | 'settings' | 'memory';

const App: React.FC = () => {
    const [currentView, setCurrentView] = useState<View>('chat');
    const { exit } = useApp();

    useInput((input, key) => {
        // Ctrl+C 退出
        if (key.ctrl && input === 'c') {
            exit();
            return;
        }

        // 数字键切换视图
        if (input === '1') setCurrentView('chat');
        if (input === '2') setCurrentView('settings');
        if (input === '3') setCurrentView('memory');
    });

    return (
        <Layout>
            {currentView === 'chat' && <Chat />}
            {currentView === 'settings' && <Settings onClose={() => setCurrentView('chat')} />}
            {currentView === 'memory' && <MemoryView onClose={() => setCurrentView('chat')} />}
        </Layout>
    );
};

export default App;
