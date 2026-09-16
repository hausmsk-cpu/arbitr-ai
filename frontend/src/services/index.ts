import api from './api'
import type { Case, Creditor, Debtor, DocumentItem, Property, RequestItem } from '../types'

/** Работа с делами о банкротстве. */
export const caseService = {
  async list(): Promise<Case[]> {
    const { data } = await api.get<Case[]>('/cases')
    return data
  },

  async create(payload: Partial<Case>): Promise<Case> {
    const { data } = await api.post<Case>('/cases', payload)
    return data
  },

  async get(caseId: string): Promise<Case> {
    const { data } = await api.get<Case>(`/cases/${caseId}`)
    return data
  },

  async update(caseId: string, payload: Partial<Case>): Promise<Case> {
    const { data } = await api.patch<Case>(`/cases/${caseId}`, payload)
    return data
  },

  async listDebtors(caseId: string): Promise<Debtor[]> {
    const { data } = await api.get<Debtor[]>(`/cases/${caseId}/debtors`)
    return data
  },

  async listCreditors(caseId: string): Promise<Creditor[]> {
    const { data } = await api.get<Creditor[]>(`/cases/${caseId}/creditors`)
    return data
  },

  async listProperties(caseId: string): Promise<Property[]> {
    const { data } = await api.get<Property[]>(`/cases/${caseId}/properties`)
    return data
  },

  async listDocuments(caseId: string): Promise<DocumentItem[]> {
    const { data } = await api.get<DocumentItem[]>(`/cases/${caseId}/documents`)
    return data
  },
}

/** Работа с запросами в госорганы. */
export const requestService = {
  async list(caseId?: string): Promise<RequestItem[]> {
    const { data } = await api.get<RequestItem[]>('/requests', {
      params: caseId ? { case_id: caseId } : {},
    })
    return data
  },

  async create(caseId: string, payload: Partial<RequestItem>): Promise<RequestItem> {
    const { data } = await api.post<RequestItem>('/requests', payload, {
      params: { case_id: caseId },
    })
    return data
  },
}