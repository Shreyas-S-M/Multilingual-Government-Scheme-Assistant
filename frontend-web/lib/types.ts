export type Language = "en" | "kn";

export interface CriterionResult {
  criterion_id: string;
  name: string;
  status: "PASS" | "FAIL" | "UNKNOWN";
  reason: string;
  source_citation?: string | null;
}

export interface SchemeResult {
  scheme_id: string;
  scheme_name: string;
  category?: string | null;
  overall_status: "PASS" | "FAIL" | "UNKNOWN";
  summary_explanation?: string | null;
  benefits_summary?: string | null;
  official_portal_url?: string | null;
  is_near_miss?: boolean;
  near_miss_reason?: string | null;
  missing_attributes?: string[];
  criteria_results?: CriterionResult[];
  failed_criteria?: CriterionResult[];
}

export interface Profile {
  age?: number | null;
  state?: string | null;
  occupation?: string | null;
  annual_income?: number | null;
  residence_type?: string | null;
  education_level?: string | null;
  gender?: string | null;
  social_category?: string | null;
  has_bpl_card?: boolean | null;
  land_ownership_ha?: number | null;
  is_student?: boolean | null;
  is_disabled?: boolean | null;
  disability_percentage?: number | null;
  unemployed_duration_months?: number | null;
  confidences?: Record<string, number>;
  source_spans?: Record<string, string>;
  field_status?: Record<string, string>;
  [key: string]: any;
}

export interface SourceReference {
  scheme_id: string;
  scheme_name: string;
  official_portal_url: string;
  source_title: string;
  last_verified_date: string;
}

export interface ChatResponse {
  reply: string;
  language: string;
  detected_language: string;
  intent: string;
  conversation_id: string;
  extracted_entities: Record<string, any>;
  updated_profile: Profile;
  recommended_schemes: SchemeResult[];
  near_miss_schemes: SchemeResult[];
  follow_up_question?: string | null;
  follow_up_target_attribute?: string | null;
  sources: SourceReference[];
  is_llm_generated: boolean;
  is_final_assessment: boolean;
  intake_completed: number;
  intake_total: number;
  has_conflicts: boolean;
  conflicting_fields: string[];
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  text: string;
  response?: ChatResponse;
}
