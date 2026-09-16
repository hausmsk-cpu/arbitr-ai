import { useQuery } from '@tanstack/react-query'
import { Button, Card, Space, Table, Tag, Typography } from 'antd'
import { useNavigate } from 'react-router-dom'
import { caseService } from '../services'
import type { Case } from '../types'

const STATUS_LABELS: Record<string, string> = {
  draft: 'Черновик',
  preparing: 'Подготовка',
  submitted: 'Подано',
  in_procedure: 'В процедуре',
  completed: 'Завершено',
  terminated: 'Прекращено',
  archived: 'Архив',
}

export function CasesPage() {
  const navigate = useNavigate()
  const { data: cases, isLoading } = useQuery({
    queryKey: ['cases'],
    queryFn: caseService.list,
  })

  const columns = [
    {
      title: '№ дела',
      dataIndex: 'case_number',
      render: (v: string | null) => v ?? '—',
    },
    {
      title: 'Суд',
      dataIndex: 'court_name',
    },
    {
      title: 'Регион',
      dataIndex: 'court_region',
    },
    {
      title: 'Статус',
      dataIndex: 'status',
      render: (v: string) => (
        <Tag color={v === 'in_procedure' ? 'green' : v === 'draft' ? 'default' : 'blue'}>
          {STATUS_LABELS[v] ?? v}
        </Tag>
      ),
    },
    {
      title: 'Действия',
      key: 'actions',
      render: (_: unknown, record: Case) => (
        <Space>
          <Button type="link" onClick={() => navigate(`/cases/${record.id}`)}>
            Открыть
          </Button>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <Space style={{ width: '100%', justifyContent: 'space-between', marginBottom: 16 }}>
        <Typography.Title level={3} style={{ margin: 0 }}>
          Дела о банкротстве
        </Typography.Title>
        <Button type="primary">Новое дело</Button>
      </Space>
      <Card>
        <Table<Case>
          rowKey="id"
          loading={isLoading}
          columns={columns}
          dataSource={cases ?? []}
          pagination={{ pageSize: 10 }}
        />
      </Card>
    </div>
  )
}