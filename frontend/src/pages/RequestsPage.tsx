import { useQuery } from '@tanstack/react-query'
import { Card, Table, Tag, Typography } from 'antd'
import { requestService } from '../services'
import type { RequestItem } from '../types'

const STATUS_COLORS: Record<string, string> = {
  draft: 'default',
  pending: 'orange',
  sent: 'blue',
  delivered: 'cyan',
  waiting: 'gold',
  partial: 'geekblue',
  response: 'green',
  rejected: 'red',
  error: 'volcano',
}

const STATUS_LABELS: Record<string, string> = {
  draft: 'Черновик',
  pending: 'Ожидает отправки',
  sent: 'Отправлено',
  delivered: 'Доставлено',
  waiting: 'Ждём ответ',
  partial: 'Частичный ответ',
  response: 'Ответ получен',
  rejected: 'Отказ',
  error: 'Ошибка',
}

export function RequestsPage() {
  const { data: requests, isLoading } = useQuery({
    queryKey: ['requests'],
    queryFn: () => requestService.list(),
  })

  const columns = [
    { title: 'Название', dataIndex: 'title' },
    { title: 'Орган', dataIndex: 'target_org' },
    {
      title: 'Тип',
      dataIndex: 'request_type',
      render: (v: string) => <Tag>{v.toUpperCase()}</Tag>,
    },
    {
      title: 'Статус',
      dataIndex: 'status',
      render: (v: string) => (
        <Tag color={STATUS_COLORS[v] ?? 'default'}>{STATUS_LABELS[v] ?? v}</Tag>
      ),
    },
    {
      title: 'Способ отправки',
      dataIndex: 'sending_method',
      render: (v: string) => v,
    },
  ]

  return (
    <div>
      <Typography.Title level={3}>Запросы в госорганы</Typography.Title>
      <Card>
        <Table<RequestItem>
          rowKey="id"
          loading={isLoading}
          columns={columns}
          dataSource={requests ?? []}
          pagination={{ pageSize: 10 }}
        />
      </Card>
    </div>
  )
}