import { useState, useEffect, useCallback } from "react";
import { api } from "../services/api";
import type { SettingsResponse } from "../types";

export function useSettings() {
  const [settings, setSettings] = useState<SettingsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<"idle" | "success" | "error">("idle");

  const loadSettings = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.getSettings();
      if (response.code === 0) {
        setSettings(response.data);
      } else {
        setError(response.message || "加载设置失败");
      }
    } catch (err: any) {
      setError(err.message || "加载设置失败");
    } finally {
      setLoading(false);
    }
  }, []);

  const updateSetting = useCallback(async (section: string, key: string, value: any) => {
    try {
      setSaving(true);
      setSaveStatus("idle");
      const response = await api.updateSettings(section, key, value);
      if (response.code === 0) {
        setSettings((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            [section]: {
              ...prev[section],
              [key]: value,
            },
          } as SettingsResponse;
        });
        setSaveStatus("success");
        setTimeout(() => setSaveStatus("idle"), 2000);
        return true;
      }
      setSaveStatus("error");
      return false;
    } catch (err: any) {
      setSaveStatus("error");
      setError(err.message || "更新设置失败");
      return false;
    } finally {
      setSaving(false);
    }
  }, []);

  useEffect(() => {
    loadSettings();
  }, [loadSettings]);

  return {
    settings,
    loading,
    error,
    saving,
    saveStatus,
    updateSetting,
    reloadSettings: loadSettings,
  };
}
