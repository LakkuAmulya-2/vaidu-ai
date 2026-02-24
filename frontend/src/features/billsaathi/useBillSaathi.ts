import { useMutation } from '@tanstack/react-query';
import api from '@/lib/api';

export interface BillAnalysisRequest {
  file: File;
  diagnosis?: string;
  patient_name?: string;
  lang?: string;
}

export interface InsuranceNavigateRequest {
  policy_file: File;
  bill_data: string;
  patient_name?: string;
  diagnosis?: string;
  lang?: string;
}

export interface DisputeLetterRequest {
  overcharge_items: string;
  hospital_name: string;
  patient_name: string;
  bill_number: string;
  bill_date: string;
  lang?: string;
}

export interface ConsumerForumRequest {
  case_details: string;
  lang?: string;
}

export interface NegotiationScriptRequest {
  overcharge_amount: number;
  hospital_name: string;
  leverage_points?: string;
  lang?: string;
}

export interface VisualQARequest {
  file: File;
  query: string;
}

export const useBillAnalysis = () => {
  return useMutation({
    mutationFn: async (data: BillAnalysisRequest) => {
      const formData = new FormData();
      formData.append('file', data.file);
      if (data.diagnosis) formData.append('diagnosis', data.diagnosis);
      if (data.patient_name) formData.append('patient_name', data.patient_name);
      formData.append('lang', data.lang || 'te');

      const response = await api.post('/analyze-bill', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data;
    },
  });
};

export const useInsuranceNavigate = () => {
  return useMutation({
    mutationFn: async (data: InsuranceNavigateRequest) => {
      const formData = new FormData();
      formData.append('policy_file', data.policy_file);
      formData.append('bill_data', data.bill_data);
      if (data.patient_name) formData.append('patient_name', data.patient_name);
      if (data.diagnosis) formData.append('diagnosis', data.diagnosis);
      formData.append('lang', data.lang || 'te');

      const response = await api.post('/insurance-navigate', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data;
    },
  });
};

export const useDisputeLetter = () => {
  return useMutation({
    mutationFn: async (data: DisputeLetterRequest) => {
      const formData = new FormData();
      formData.append('overcharge_items', data.overcharge_items);
      formData.append('hospital_name', data.hospital_name);
      formData.append('patient_name', data.patient_name);
      formData.append('bill_number', data.bill_number);
      formData.append('bill_date', data.bill_date);
      formData.append('lang', data.lang || 'te');

      const response = await api.post('/dispute-letter', formData);
      return response.data;
    },
  });
};

export const useConsumerForum = () => {
  return useMutation({
    mutationFn: async (data: ConsumerForumRequest) => {
      const formData = new FormData();
      formData.append('case_details', data.case_details);
      formData.append('lang', data.lang || 'te');

      const response = await api.post('/consumer-forum-guidance', formData);
      return response.data;
    },
  });
};

export const useNegotiationScript = () => {
  return useMutation({
    mutationFn: async (data: NegotiationScriptRequest) => {
      const formData = new FormData();
      formData.append('overcharge_amount', data.overcharge_amount.toString());
      formData.append('hospital_name', data.hospital_name);
      formData.append('leverage_points', data.leverage_points || '{}');
      formData.append('lang', data.lang || 'te');

      const response = await api.post('/negotiation-script', formData);
      return response.data;
    },
  });
};

export const usePatientRights = () => {
  return useMutation({
    mutationFn: async (lang: string = 'te') => {
      const response = await api.get(`/patient-rights?lang=${lang}`);
      return response.data;
    },
  });
};

export const useVisualQA = () => {
  return useMutation({
    mutationFn: async (data: VisualQARequest) => {
      const formData = new FormData();
      formData.append('file', data.file);
      formData.append('query', data.query);

      const response = await api.post('/visual-qa', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data;
    },
  });
};
