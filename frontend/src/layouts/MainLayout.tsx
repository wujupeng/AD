import { Outlet } from 'react-router-dom'
import { Layout, Menu } from 'antd'
import {
  TeamOutlined,
  SafetyOutlined,
  FolderOutlined,
  PrinterOutlined,
  MailOutlined,
  AuditOutlined,
  DashboardOutlined,
  SettingOutlined,
  CloudServerOutlined,
  KeyOutlined,
  SecurityScanOutlined,
  CloudOutlined,
  AlertOutlined,
  ApiOutlined,
  LockOutlined,
  GlobalOutlined,
  WifiOutlined,
  IdcardOutlined,
} from '@ant-design/icons'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

const { Sider, Header, Content } = Layout

const menuItems = [
  { key: '/org', icon: <TeamOutlined />, label: '组织架构' },
  { key: '/permissions', icon: <SafetyOutlined />, label: '权限管理' },
  { key: '/dfs', icon: <FolderOutlined />, label: '文件服务' },
  { key: '/print', icon: <PrinterOutlined />, label: '打印服务' },
  { key: '/mail', icon: <MailOutlined />, label: '邮件通讯' },
  { key: '/audit', icon: <AuditOutlined />, label: '审计合规' },
  { key: '/health', icon: <DashboardOutlined />, label: '系统监控' },
  { key: '/settings', icon: <SettingOutlined />, label: '系统配置' },
  { type: 'divider' as const },
  {
    key: 'enterprise-group',
    icon: <CloudServerOutlined />,
    label: '企业级管理',
    children: [
      { key: '/dc-mgmt', icon: <CloudServerOutlined />, label: 'DC管理' },
      { key: '/dfs-repl', icon: <FolderOutlined />, label: 'DFS复制' },
      { key: '/pki', icon: <KeyOutlined />, label: 'PKI证书' },
      { key: '/tier-security', icon: <SecurityScanOutlined />, label: 'Tier安全' },
      { key: '/cloud-phase', icon: <CloudOutlined />, label: '云化路线' },
      { key: '/alert-panel', icon: <AlertOutlined />, label: '告警面板' },
      { key: '/sdwan', icon: <ApiOutlined />, label: 'SD-WAN' },
      { key: '/secure-print', icon: <LockOutlined />, label: '安全打印' },
      { key: '/remote-access', icon: <GlobalOutlined />, label: '远程访问' },
      { key: '/vpn-mgmt', icon: <WifiOutlined />, label: 'VPN管理' },
    ],
  },
  {
    key: 'identity-group',
    icon: <IdcardOutlined />,
    label: '统一数字身份中心',
    children: [
      { key: '/identity-center', icon: <IdcardOutlined />, label: '身份中心' },
      { key: '/hr-onboarding', icon: <TeamOutlined />, label: 'HR入职' },
      { key: '/hr-offboarding', icon: <TeamOutlined />, label: 'HR离职' },
      { key: '/hr-transfer', icon: <TeamOutlined />, label: 'HR调岗' },
      { key: '/identity-lifecycle', icon: <AuditOutlined />, label: '身份生命周期' },
    ],
  },
]

export default function MainLayout() {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuthStore()

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key)
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={200} theme="dark">
        <div style={{ height: 48, margin: 16, color: '#fff', fontSize: 16, fontWeight: 'bold' }}>
          Htkis-Cloud-ADCS
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          defaultOpenKeys={['enterprise-group', 'identity-group']}
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            background: '#fff',
            padding: '0 24px',
            display: 'flex',
            justifyContent: 'flex-end',
            alignItems: 'center',
            gap: 16,
          }}
        >
          <span>{user?.displayName || ''}</span>
          <a onClick={handleLogout}>退出登录</a>
        </Header>
        <Content style={{ margin: 24 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}