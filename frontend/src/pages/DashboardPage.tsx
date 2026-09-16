import { Card, Col, Row, Statistic, Typography } from 'antd'
import {
  AccountBookOutlined,
  AlertOutlined,
  FileProtectOutlined,
  RiseOutlined,
} from '@ant-design/icons'

export function DashboardPage() {
  return (
    <div>
      <Typography.Title level={3}>Дашборд</Typography.Title>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Активные дела"
              value={12}
              prefix={<AccountBookOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Запросы в работе"
              value={48}
              prefix={<RiseOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Ближайшие сроки"
              value={5}
              valueStyle={{ color: '#cf1322' }}
              prefix={<AlertOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Сгенерировано документов"
              value={137}
              prefix={<FileProtectOutlined />}
            />
          </Card>
        </Col>
      </Row>
    </div>
  )
}