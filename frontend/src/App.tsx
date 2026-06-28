import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import MainLayout from './layouts/MainLayout'
import LoginPage from './pages/LoginPage'
import UserListPage from './pages/UserListPage'
import PermissionCheckPage from './pages/PermissionCheckPage'
import DfsBrowserPage from './pages/DfsBrowserPage'
import PrintPage from './pages/PrintPage'
import AuditLogPage from './pages/AuditLogPage'
import HealthMonitorPage from './pages/HealthMonitorPage'
import DcManagementPage from './pages/DcManagementPage'
import DfsReplicationPage from './pages/DfsReplicationPage'
import PkiManagementPage from './pages/PkiManagementPage'
import TierSecurityPage from './pages/TierSecurityPage'
import CloudPhasePage from './pages/CloudPhasePage'
import AlertPanelPage from './pages/AlertPanelPage'
import SdwanStatusPage from './pages/SdwanStatusPage'
import SecurePrintPage from './pages/SecurePrintPage'
import RemoteAccessPage from './pages/RemoteAccessPage'
import VpnManagementPage from './pages/VpnManagementPage'
import IdentityCenterPage from './pages/IdentityCenterPage'
import HrOnboardingPage from './pages/HrOnboardingPage'
import HrOffboardingPage from './pages/HrOffboardingPage'
import HrTransferPage from './pages/HrTransferPage'
import IdentityLifecyclePage from './pages/IdentityLifecyclePage'
import SettingsPage from './pages/SettingsPage'
import MailPage from './pages/MailPage'

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<MainLayout />}>
            <Route index element={<Navigate to="/org" replace />} />
            <Route path="org" element={<UserListPage />} />
            <Route path="permissions" element={<PermissionCheckPage />} />
            <Route path="dfs" element={<DfsBrowserPage />} />
            <Route path="print" element={<PrintPage />} />
            <Route path="mail" element={<MailPage />} />
            <Route path="audit" element={<AuditLogPage />} />
            <Route path="health" element={<HealthMonitorPage />} />
            <Route path="dc-mgmt" element={<DcManagementPage />} />
            <Route path="dfs-repl" element={<DfsReplicationPage />} />
            <Route path="pki" element={<PkiManagementPage />} />
            <Route path="tier-security" element={<TierSecurityPage />} />
            <Route path="cloud-phase" element={<CloudPhasePage />} />
            <Route path="alert-panel" element={<AlertPanelPage />} />
            <Route path="sdwan" element={<SdwanStatusPage />} />
            <Route path="secure-print" element={<SecurePrintPage />} />
            <Route path="remote-access" element={<RemoteAccessPage />} />
            <Route path="vpn-mgmt" element={<VpnManagementPage />} />
            <Route path="identity-center" element={<IdentityCenterPage />} />
            <Route path="hr-onboarding" element={<HrOnboardingPage />} />
            <Route path="hr-offboarding" element={<HrOffboardingPage />} />
            <Route path="hr-transfer" element={<HrTransferPage />} />
            <Route path="identity-lifecycle" element={<IdentityLifecyclePage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  )
}

export default App