/** Типы данных для интеграций с бэкендом Arbitr AI. */

export interface Case {
  id: string
  case_number: string | null
  court_name: string
  court_region: string
  status: string
  procedure_type: string | null
  application_date: string | null
  procedure_start_date: string | null
  procedure_end_date: string | null
  created_at: string
  updated_at: string
}

export interface Debtor {
  id: string
  full_name: string
  inn: string | null
  snils: string | null
  birth_date: string | null
  address: string | null
}

export interface Creditor {
  id: string
  name: string
  inn: string | null
  kpp: string | null
  is_legal_entity: boolean
  claim_amount: number
  claim_currency: string
  claim_basis: string | null
  status_in_registry: string | null
}

export interface Property {
  id: string
  property_type: string
  description: string | null
  address: string | null
  cadastral_number: string | null
  estimated_value: number | null
  sale_value: number | null
  is_preserved: boolean
}

export interface DocumentItem {
  id: string
  title: string
  doc_type: string
  mime_type: string
  size_bytes: number
  generated_by_ai: boolean
  version: number
  created_at: string
}

export interface RequestItem {
  id: string
  request_type: string
  title: string
  target_org: string
  status: string
  sending_method: string
  content: string | null
  external_tracking: string | null
  response_data: string | null
  sent_at: string | null
  response_at: string | null
  deadline: string | null
  created_at: string
}

export interface User {
  id: string
  email: string
  full_name: string
  role: string
  created_at: string
}