import { useMutation } from '@tanstack/react-query';
import api, { ApiResponse } from '@/lib/api';

interface DiabetesParams {
  query: string;
  age: number;
  check_type: string;
  lang: string;
  file?: File;
}

export const useDiabetes = () => {
  return useMutation({
    mutationFn: async ({ file, ...data }: DiabetesParams): Promise<ApiResponse> => {
      const formData = new FormData();
      Object.entries(data).forEach(([key, value]) => {
        formData.append(key, String(value));
      });
      if (file) {
        formData.append('file', file);
      }
      return api.post('/diabetes', formData);
    },
  });
};