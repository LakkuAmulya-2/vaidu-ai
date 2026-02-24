import { useMutation } from '@tanstack/react-query';
import api, { ApiResponse } from '@/lib/api';

interface SkinParams {
  file: File;
  area: string;
  lang: string;
}

export const useSkin = () => {
  return useMutation({
    mutationFn: async ({ file, area, lang }: SkinParams): Promise<ApiResponse> => {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('area', area);
      formData.append('lang', lang);
      return api.post('/analyze/skin', formData);
    },
  });
};