import { useState, useCallback } from 'react';
import { api } from '../services/api';

export type MemoryLayer = 'global' | 'project' | 'task' | 'session' | 'checkpoint';

interface MemoryData {
    layer: string;
    content: string;
    updated_at: string;
}

export function useMemory(project: string = 'default') {
    const [activeLayer, setActiveLayer] = useState<MemoryLayer>('global');
    const [memoryData, setMemoryData] = useState<Record<string, MemoryData>>({});
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const loadMemory = useCallback(async (layer: MemoryLayer) => {
        try {
            setLoading(true);
            setError(null);
            const response = await api.getMemory(project, layer);
            if (response.code === 0) {
                setMemoryData(prev => ({
                    ...prev,
                    [layer]: response.data
                }));
            }
        } catch (err) {
            setError('加载 Memory 失败');
        } finally {
            setLoading(false);
        }
    }, [project]);

    const switchLayer = useCallback((layer: MemoryLayer) => {
        setActiveLayer(layer);
        if (!memoryData[layer]) {
            loadMemory(layer);
        }
    }, [memoryData, loadMemory]);

    const refresh = useCallback(() => {
        loadMemory(activeLayer);
    }, [activeLayer, loadMemory]);

    return {
        activeLayer,
        memoryData,
        loading,
        error,
        switchLayer,
        refresh,
        currentContent: memoryData[activeLayer]?.content || '',
        currentUpdatedAt: memoryData[activeLayer]?.updated_at || '',
    };
}
