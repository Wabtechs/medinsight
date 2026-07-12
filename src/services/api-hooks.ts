import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from './api';

function getToken(): string {
  return localStorage.getItem('medinsight-access-token') || '';
}

export function useLogin() {
  return useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      api.login(email, password),
    onSuccess: (data) => {
      localStorage.setItem('medinsight-access-token', data.access_token);
      localStorage.setItem('medinsight-refresh-token', data.refresh_token);
    },
  });
}

export function useMe() {
  return useQuery({
    queryKey: ['auth', 'me'],
    queryFn: () => api.get('/auth/me', getToken()),
    enabled: !!localStorage.getItem('medinsight-access-token'),
    retry: false,
  });
}

export function useFacilities() {
  return useQuery({
    queryKey: ['facilities'],
    queryFn: () => api.get<{ items: unknown[]; total: number }>('/facilities', getToken()),
  });
}

export function usePatients() {
  return useQuery({
    queryKey: ['patients'],
    queryFn: () => api.get<{ items: unknown[]; total: number }>('/patients', getToken()),
  });
}

export function useClinicalCases() {
  return useQuery({
    queryKey: ['clinical-cases'],
    queryFn: () => api.get<{ items: unknown[]; total: number }>('/clinical-cases', getToken()),
  });
}

export function useCreateClinicalCase() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Record<string, unknown>) =>
      api.post('/clinical-cases', data, getToken()),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clinical-cases'] });
    },
  });
}

export function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: () => api.get<{ items: unknown[]; total: number }>('/users', getToken()),
  });
}

export function useAuditLogs() {
  return useQuery({
    queryKey: ['audit'],
    queryFn: () => api.get<{ items: unknown[]; total: number }>('/audit', getToken()),
  });
}

export function useDashboardStats() {
  return useQuery({
    queryKey: ['dashboard', 'stats'],
    queryFn: () => api.get<{
      total_cases: number;
      total_patients: number;
      total_facilities: number;
      resolution_rate: number;
      recent_cases: unknown[];
    }>('/clinical-cases/stats', getToken()),
  });
}
