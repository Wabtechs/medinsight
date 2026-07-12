export interface SyncQueueItem {
  id: string;
  entityType: 'patient' | 'clinical_case' | 'audit_log';
  entityId: string;
  action: 'create' | 'update' | 'delete';
  payload: Record<string, unknown>;
  status: 'pending' | 'synced' | 'failed';
  errorMessage?: string;
  createdAt: string;
  syncedAt?: string;
}

const DB_NAME = 'medinsight-sync';
const DB_VERSION = 1;
const STORE_NAME = 'sync_queue';

function openDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
    request.onupgradeneeded = (event) => {
      const db = (event.target as IDBOpenDBRequest).result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        const store = db.createObjectStore(STORE_NAME, { keyPath: 'id' });
        store.createIndex('status', 'status', { unique: false });
        store.createIndex('entityType', 'entityType', { unique: false });
      }
    };
  });
}

export const syncEngine = {
  async addToQueue(item: Omit<SyncQueueItem, 'id' | 'status' | 'createdAt'>): Promise<SyncQueueItem> {
    const db = await openDB();
    const entry: SyncQueueItem = {
      ...item,
      id: crypto.randomUUID(),
      status: 'pending',
      createdAt: new Date().toISOString(),
    };
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, 'readwrite');
      tx.objectStore(STORE_NAME).put(entry);
      tx.oncomplete = () => resolve(entry);
      tx.onerror = () => reject(tx.error);
    });
  },

  async getPendingItems(): Promise<SyncQueueItem[]> {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, 'readonly');
      const index = tx.objectStore(STORE_NAME).index('status');
      const request = index.getAll('pending');
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  },

  async markSynced(id: string): Promise<void> {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, 'readwrite');
      const store = tx.objectStore(STORE_NAME);
      const get = store.get(id);
      get.onsuccess = () => {
        const item = get.result;
        if (item) {
          item.status = 'synced';
          item.syncedAt = new Date().toISOString();
          store.put(item);
        }
      };
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  },

  async markFailed(id: string, error: string): Promise<void> {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, 'readwrite');
      const store = tx.objectStore(STORE_NAME);
      const get = store.get(id);
      get.onsuccess = () => {
        const item = get.result;
        if (item) {
          item.status = 'failed';
          item.errorMessage = error;
          store.put(item);
        }
      };
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  },

  async clearSynced(): Promise<void> {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, 'readwrite');
      const index = tx.objectStore(STORE_NAME).index('status');
      const request = index.openCursor('synced');
      request.onsuccess = (event) => {
        const cursor = (event.target as IDBRequest).result;
        if (cursor) {
          cursor.delete();
          cursor.continue();
        }
      };
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  },

  async getPendingCount(): Promise<number> {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, 'readonly');
      const index = tx.objectStore(STORE_NAME).index('status');
      const request = index.count('pending');
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  },

  async syncAll(apiBaseUrl: string, token: string): Promise<{ synced: number; failed: number }> {
    const pending = await this.getPendingItems();
    let synced = 0;
    let failed = 0;

    for (const item of pending) {
      try {
        const endpoint = item.entityType === 'clinical_case' ? '/clinical-cases' :
                         item.entityType === 'patient' ? '/patients' : '/audit';
        const method = item.action === 'delete' ? 'DELETE' : item.action === 'update' ? 'PUT' : 'POST';
        const url = item.action === 'delete' || item.action === 'update'
          ? `${endpoint}/${item.entityId}`
          : endpoint;

        const response = await fetch(`${apiBaseUrl}${url}`, {
          method,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: item.action !== 'delete' ? JSON.stringify(item.payload) : undefined,
        });

        if (response.ok) {
          await this.markSynced(item.id);
          synced++;
        } else {
          const error = await response.text();
          await this.markFailed(item.id, error);
          failed++;
        }
      } catch (error) {
        await this.markFailed(item.id, String(error));
        failed++;
      }
    }

    return { synced, failed };
  },
};
