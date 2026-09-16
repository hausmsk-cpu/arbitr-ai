import { Layout, Menu, Typography } from 'antd'
import {
  DashboardOutlined,
  FileSearchOutlined,
  FolderOpenOutlined,
  SendOutlined,
  SettingOutlined,
} from '@ant-design/icons'
import { Route, Routes, useNavigate } from 'react-router-dom'
import { CasesPage } from './pages/CasesPage'
import { DashboardPage } from './pages/DashboardPage'
import { CaseDetailPage } from './pages/CaseDetailPage'
import { RequestsPage } from './pages/RequestsPage'

const { Header, Sider, Content } = Layout

function App() {
  const navigate = useNavigate()

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider breakpoint="lg" collapsedWidth="80">
        <div style={{ color: '#fff', padding: 16, fontSize: 18, fontWeight: 700 }}>
          Arbitr AI
        </div>
        <Menu
          theme="dark"
          mode="inline"
          defaultSelectedKeys={['dashboard']}
          onClick={({ key }) => navigate(key)}
          items={[
            { key: 'dashboard', icon: <DashboardOutlined />, label: 'Дашборд' },
            { key: 'cases', icon: <FolderOpenOutlined />, label: 'Дела' },
            { key: 'requests', icon: <SendOutlined />, label: 'Запросы' },
            { key: 'documents', icon: <FileSearchOutlined />, label: 'Документы' },
            { key: 'settings', icon: <SettingOutlined />, label: 'Настройки' },
          ]}
        />
      </Sider>
      <Layout>
        <Header style={{ background: '#fff', paddingInline: 24 }}>
          <Typography.Title level={4} style={{ margin: '16px 0' }}>
            Кабинет финансового управляющего
          </Typography.Title>
        </Header>
        <Content style={{ margin: 24 }}>
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/cases" element={<CasesPage />} />
            <Route path="/cases/:caseId" element={<CaseDetailPage />} />
            <Route path="/requests" element={<RequestsPage />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  )
}

export default App