import { useMutation } from '@tanstack/react-query';
import api, { ApiResponse, createFormData } from '@/lib/api';

interface GovtSchemesParams {
  query: string;
  lang: string;
}

export const useGovtSchemes = () => {
  return useMutation({
    mutationFn: async (params: GovtSchemesParams): Promise<ApiResponse> => {
      const formData = createFormData(params);
      return api.post('/govt-schemes', formData);
    },
  });
};