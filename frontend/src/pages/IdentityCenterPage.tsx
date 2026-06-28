import { Tabs } from 'antd'
import IdentitySourcePolicyConfig from '../components/identity/IdentitySourcePolicyConfig'
import EntraIdExtensionStatus from '../components/identity/EntraIdExtensionStatus'
import BadgeIdentityManager from '../components/identity/BadgeIdentityManager'
import PrintConvergenceManager from '../components/identity/PrintConvergenceManager'
import SamlOidcAppManager from '../components/identity/SamlOidcAppManager'
import Wifi8021xPolicyManager from '../components/identity/Wifi8021xPolicyManager'
import AutopilotProfileManager from '../components/identity/AutopilotProfileManager'
import ConditionalAccessRuleManager from '../components/identity/ConditionalAccessRuleManager'
import LifecycleAuditPanel from '../components/identity/LifecycleAuditPanel'

export default function IdentityCenterPage() {
  return (
    <Tabs defaultActiveKey="source" items={[
      { key: 'source', label: '身份源策略', children: <IdentitySourcePolicyConfig /> },
      { key: 'entra', label: 'Entra ID扩展', children: <EntraIdExtensionStatus /> },
      { key: 'badge', label: '工牌身份', children: <BadgeIdentityManager /> },
      { key: 'print', label: '打印融合', children: <PrintConvergenceManager /> },
      { key: 'saml', label: 'SAML/OIDC应用', children: <SamlOidcAppManager /> },
      { key: 'wifi', label: 'Wi-Fi 802.1X', children: <Wifi8021xPolicyManager /> },
      { key: 'autopilot', label: 'Autopilot', children: <AutopilotProfileManager /> },
      { key: 'ca', label: '条件访问', children: <ConditionalAccessRuleManager /> },
      { key: 'audit', label: '生命周期审计', children: <LifecycleAuditPanel /> },
    ]} />
  )
}
