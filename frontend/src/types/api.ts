export interface ApiResponse {
  success: boolean;
  response: string;
  severity?: 'GREEN' | 'YELLOW' | 'RED';
  [key: string]: any;
}

export interface TriageRequest {
  symptoms: string;
  age: number;
  is_pregnant: boolean;
  lang: string;
}

export interface PrescriptionRequest {
  file: File;
  lang: string;
}

export interface MentalHealthRequest {
  query: string;
  lang: string;
}

export interface ChildHealthRequest {
  query: string;
  age_months: number;
  weight_kg: number;
  lang: string;
}

export interface InfectiousRequest {
  symptoms: string;
  fever_days: number;
  lang: string;
}

export interface GovtSchemesRequest {
  query: string;
  lang: string;
}