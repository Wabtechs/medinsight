import { useState, useEffect, useCallback, useRef } from 'react';
import { syncEngine } from '@/services/sync-engine';
import { useOnlineStatus } from './use-online-status';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export function useSync() {
  const { isOnline, wasOffline } = useOnlineStatus();
  const [pendingCount, setPendingCount] = useState(0);
  const [isSyncing, setIsSyncing] = useState(false);
  const [lastSyncTime, setLastSyncTime] = useState<string | null>(null);
  const mountedRef = useRef(true);

  const refreshPendingCount = useCallback(async () => {
    const count = await syncEngine.getPendingCount();
    if (mountedRef.current) {
      setPendingCount(count);
    }
  }, []);

  const syncNow = useCallback(async () => {
    if (!isOnline || isSyncing) return;
    setIsSyncing(true);
    try {
      const token = localStorage.getItem('medinsight-access-token');
      if (!token) return;
      const result = await syncEngine.syncAll(API_BASE, token);
      await syncEngine.clearSynced();
      await refreshPendingCount();
      if (mountedRef.current) {
        setLastSyncTime(new Date().toISOString());
      }
      return result;
    } finally {
      if (mountedRef.current) {
        setIsSyncing(false);
      }
    }
  }, [isOnline, isSyncing, refreshPendingCount]);

  useEffect(() => {
    mountedRef.current = true;
    return () => { mountedRef.current = false; };
  }, []);

  useEffect(() => {
    if (wasOffline && isOnline && pendingCount > 0) {
      const timer = setTimeout(() => { syncNow(); }, 0);
      return () => clearTimeout(timer);
    }
  }, [wasOffline, isOnline, pendingCount, syncNow]);

  useEffect(() => {
    const timer = setTimeout(() => { refreshPendingCount(); }, 0);
    return () => clearTimeout(timer);
  }, [refreshPendingCount]);

  return {
    isOnline,
    isSyncing,
    pendingCount,
    lastSyncTime,
    syncNow,
    refreshPendingCount,
  };
}
