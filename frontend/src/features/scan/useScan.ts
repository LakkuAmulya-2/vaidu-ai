import { useMutation } from '@tanstack/react-query';
import api, { ApiResponse } from '@/lib/api';

interface ScanParams {
  file: File;
  scan_type: string;
  lang: string;
}

export const useScan = () => {
  return useMutation({
    mutationFn: async ({ file, scan_type, lang }: ScanParams): Promise<ApiResponse> => {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('scan_type', scan_type);
      formData.append('lang', lang);
      return api.post('/analyze/scan', formData);
    },
  });
};