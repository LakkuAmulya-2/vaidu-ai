import { useMutation } from '@tanstack/react-query';
import api, { ApiResponse, createFormData } from '@/lib/api';

interface MentalHealthParams {
  query: string;
  lang: string;
}

export const useMentalHealth = () => {
  return useMutation({
    mutationFn: async (params: MentalHealthParams): Promise<ApiResponse> => {
      const formData = createFormData(params);
      return api.post('/mental-health', formData);
    },
  });
};
