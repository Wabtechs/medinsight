import { useCallback } from 'react';
import { syncEngine } from '@/services/sync-engine';
import { useOnlineStatus } from './use-online-status';

export function useOfflineStorage() {
  const { isOnline } = useOnlineStatus();

  const refreshPendingCount = useCallback(async () => {
    return syncEngine.getPendingCount();
  }, []);

  const savePatientOffline = useCallback(async (patientData: Record<string, unknown>) => {
    const id = crypto.randomUUID();
    await syncEngine.addToQueue({
      entityType: 'patient',
      entityId: id,
      action: 'create',
      payload: { ...patientData, id },
    });
    await refreshPendingCount();
    return id;
  }, [refreshPendingCount]);

  const saveCaseOffline = useCallback(async (caseData: Record<string, unknown>) => {
    const id = crypto.randomUUID();
    await syncEngine.addToQueue({
      entityType: 'clinical_case',
      entityId: id,
      action: 'create',
      payload: { ...caseData, id },
    });
    await refreshPendingCount();
    return id;
  }, [refreshPendingCount]);

  const updateCaseOffline = useCallback(async (id: string, caseData: Record<string, unknown>) => {
    await syncEngine.addToQueue({
      entityType: 'clinical_case',
      entityId: id,
      action: 'update',
      payload: { ...caseData, id },
    });
    await refreshPendingCount();
  }, [refreshPendingCount]);

  return {
    isOnline,
    savePatientOffline,
    saveCaseOffline,
    updateCaseOffline,
  };
}
