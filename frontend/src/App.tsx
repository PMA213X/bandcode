import React, { useState, useCallback } from 'react';
import { useInput, useApp } from 'ink';
import Chat from './components/Chat';
import Settings from './components/Settings';
import MemoryView from './components/MemoryView';
import Layout from './components/Layout';

type View = 'chat' | 'settings' | 'memory';

const App: React.FC = () => {
    const [currentView, setCurrentView] = useState<View>('chat');
    const { exit } = useApp();

    const handleViewChange = useCallback((view: View) => {
        setCurrentView(view);
    }, []);

    useInput((input, key) => {
        // Ctrl+C 退出
        if (key.ctrl && input === 'c') {
            exit();
            return;
        }

        // 只在聊天视图时用数字键切换视图（避免与 Chat 输入冲突）
        if (currentView === 'chat') {
            if (input === '1') setCurrentView('chat');
            if (input === '2') setCurrentView('settings');
            if (input === '3') setCurrentView('memory');
        }
    });

    return (
        <Layout currentView={currentView} onViewChange={handleViewChange}>
            {currentView === 'chat' && <Chat />}
            {currentView === 'settings' && <Settings onClose={() => setCurrentView('chat')} />}
            {currentView === 'memory' && <MemoryView onClose={() => setCurrentView('chat')} />}
        </Layout>
    );
};

export default App;
