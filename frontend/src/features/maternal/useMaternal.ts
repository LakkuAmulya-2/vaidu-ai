import { useMutation } from '@tanstack/react-query';
import api, { ApiResponse, createFormData } from '@/lib/api';

interface MaternalParams {
  query: string;
  week: number;
  lang: string;
}

export const useMaternal = () => {
  return useMutation({
    mutationFn: async (params: MaternalParams): Promise<ApiResponse> => {
      const formData = createFormData(params);
      return api.post('/maternal', formData);
    },
  });
};