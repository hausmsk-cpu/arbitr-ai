import { useQuery } from '@tanstack/react-query'
import { Card, Col, Descriptions, Row, Spin, Tabs, Typography } from 'antd'
import { useParams } from 'react-router-dom'
import { caseService } from '../services'

export function CaseDetailPage() {
  const { caseId } = useParams<{ caseId: string }>()

  const { data: caseData, isLoading: caseLoading } = useQuery({
    queryKey: ['case', caseId],
    queryFn: () => caseService.get(caseId!),
    enabled: !!caseId,
  })

  const { data: debtors } = useQuery({
    queryKey: ['case-debtors', caseId],
    queryFn: () => caseService.listDebtors(caseId!),
    enabled: !!caseId,
  })

  const { data: creditors } = useQuery({
    queryKey: ['case-creditors', caseId],
    queryFn: () => caseService.listCreditors(caseId!),
    enabled: !!caseId,
  })

  const { data: documents } = useQuery({
    queryKey: ['case-documents', caseId],
    queryFn: () => caseService.listDocuments(caseId!),
    enabled: !!caseId,
  })

  if (caseLoading || !caseData) {
    return <Spin size="large" style={{ display: 'block', margin: '40px auto' }} />
  }

  return (
    <div>
      <Typography.Title level={3}>
        Дело {caseData.case_number ?? '(без номера)'}
      </Typography.Title>
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Card title="Информация о деле">
            <Descriptions column={2}>
              <Descriptions.Item label="Суд">
                {caseData.court_name}
              </Descriptions.Item>
              <Descriptions.Item label="Регион">
                {caseData.court_region}
              </Descriptions.Item>
              <Descriptions.Item label="Статус">
                {caseData.status}
              </Descriptions.Item>
              <Descriptions.Item label="Процедура">
                {caseData.procedure_type ?? '—'}
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>
      </Row>
      <Tabs
        items={[
          {
            key: 'debtors',
            label: 'Должники',
            children: (
              <Card>
                {debtors?.length
                  ? debtors.map((d) => (
                      <div key={d.id}>
                        <strong>{d.full_name}</strong> · ИНН {d.inn ?? '—'}
                      </div>
                    ))
                  : 'Должники не добавлены'}
              </Card>
            ),
          },
          {
            key: 'creditors',
            label: 'Кредиторы',
            children: (
              <Card>
                {creditors?.length
                  ? creditors.map((c) => (
                      <div key={c.id}>
                        <strong>{c.name}</strong> · {c.claim_amount} {c.claim_currency}
                      </div>
                    ))
                  : 'Кредиторы не добавлены'}
              </Card>
            ),
          },
          {
            key: 'documents',
            label: 'Документы',
            children: (
              <Card>
                {documents?.length
                  ? documents.map((d) => (
                      <div key={d.id}>
                        {d.title} {d.generated_by_ai ? '(AI)' : ''}
                      </div>
                    ))
                  : 'Документы не загружены'}
              </Card>
            ),
          },
        ]}
      />
    </div>
  )
}