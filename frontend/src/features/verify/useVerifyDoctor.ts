import { useQuery } from '@tanstack/react-query';
import api, { ApiResponse } from '@/lib/api';

interface VerifyParams {
  name?: string;
  reg?: string;
}

export const useVerifyDoctor = (params: VerifyParams) => {
  return useQuery({
    queryKey: ['verifyDoctor', params],
    queryFn: async (): Promise<ApiResponse> => {
      const searchParams = new URLSearchParams();
      if (params.name) searchParams.append('name', params.name);
      if (params.reg) searchParams.append('reg', params.reg);
      return api.get(`/verify/doctor?${searchParams.toString()}`);
    },
    enabled: !!(params.name || params.reg),
  });
};