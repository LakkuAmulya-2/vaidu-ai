import { useMutation } from '@tanstack/react-query';
import api, { ApiResponse, createFormData } from '@/lib/api';

interface InfectiousParams {
  symptoms: string;
  fever_days: number;
  lang: string;
}

export const useInfectious = () => {
  return useMutation({
    mutationFn: async (params: InfectiousParams): Promise<ApiResponse> => {
      const formData = createFormData(params);
      return api.post('/infectious', formData);
    },
  });
};