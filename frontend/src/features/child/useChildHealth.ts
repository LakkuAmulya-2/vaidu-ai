import { useMutation } from '@tanstack/react-query';
import api, { ApiResponse, createFormData } from '@/lib/api';

interface ChildHealthParams {
  query: string;
  age_months: number;
  weight_kg: number;
  lang: string;
}

export const useChildHealth = () => {
  return useMutation({
    mutationFn: async (params: ChildHealthParams): Promise<ApiResponse> => {
      const formData = createFormData(params);
      return api.post('/child-health', formData);
    },
  });
};