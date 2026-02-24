import { useMutation } from '@tanstack/react-query';
import api, { ApiResponse, createFormData } from '@/lib/api';

interface TriageParams {
  symptoms: string;
  age: number;
  is_pregnant: boolean;
  lang: string;
}

export const useTriage = () => {
  return useMutation({
    mutationFn: async (params: TriageParams): Promise<ApiResponse> => {
      const formData = createFormData(params);
      return api.post('/triage', formData);
    },
  });
};