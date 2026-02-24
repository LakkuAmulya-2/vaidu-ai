import { useMutation } from '@tanstack/react-query';
import api, { ApiResponse } from '@/lib/api';

interface PrescriptionParams {
  file: File;
  lang: string;
}

export const usePrescription = () => {
  return useMutation({
    mutationFn: async ({ file, lang }: PrescriptionParams): Promise<ApiResponse> => {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('lang', lang);
      return api.post('/analyze/prescription', formData);
    },
  });
};