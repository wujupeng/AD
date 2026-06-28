import { Card, Table, Tag, Statistic, Row, Col } from 'antd'
import { useEffect, useState } from 'react'
import client from '../api/client'

interface VpnSession {
  session_id: string
  user_account: string
  device_hostname: string | null
  user_site: string | null
  tunnel_type: string
  connection_time: string | null
  auth_method: string | null
  is_active: boolean
  bytes_in: number
  bytes_out: number
}

interface VpnPolicy {
  policy_id: string
  policy_type: string
  policy_name: string
  policy_config: Record<string, unknown>
  is_enabled: boolean
}

export default function VpnManagementPage() {
  const [sessions, setSessions] = useState<VpnSession[]>([])
  const [policies, setPolicies] = useState<VpnPolicy[]>([])
  const [kerberosStats, setKerberosStats] = useState<Record<string, unknown> | null>(null)
  const [auditLogs, setAuditLogs] = useState<Record<string, unknown>[]>([])

  const fetchSessions = async () => {
    try { const { data } = await client.get('/v1/enterprise/vpn/sessions'); if (data.code === 0) setSessions(data.data) } catch {}
  }
  const fetchPolicies = async () => {
    try { const { data } = await client.get('/v1/enterprise/vpn/policies'); if (data.code === 0) setPolicies(data.data) } catch {}
  }
  const fetchKerberos = async () => {
    try { const { data } = await client.get('/v1/enterprise/vpn/kerberos-recovery'); if (data.code === 0) setKerberosStats(data.data) } catch {}
  }
  const fetchAuditLog = async () => {
    try { const { data } = await client.get('/v1/enterprise/vpn/audit-log'); if (data.code === 0) setAuditLogs(data.data) } catch {}
  }

  useEffect(() => { fetchSessions(); fetchPolicies(); fetchKerberos(); fetchAuditLog() }, [])

  const tunnelColor = (t: string) => t === 'dual_tunnel' ? 'green' : t === 'device_tunnel' ? 'blue' : 'orange'

  return (
    <div>
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col span={8}>
          <Card><Statistic title="Kerberos恢复(24h)" value={Number(kerberosStats?.kerberos_recovered || 0)} valueStyle={{ color: '#3f8600' }} /></Card>
        </Col>
        <Col span={8}>
          <Card><Statistic title="恢复失败(24h)" value={Number(kerberosStats?.kerberos_recovery_failed || 0)} valueStyle={{ color: '#cf1322' }} /></Card>
        </Col>
        <Col span={8}>
          <Card><Statistic title="NTLM降级(24h)" value={Number(kerberosStats?.ntlm_fallback || 0)} valueStyle={{ color: '#fa8c16' }} /></Card>
        </Col>
      </Row>

      <Card title="VPN会话">
        <Table dataSource={sessions} columns={[
          { title: '用户', dataIndex: 'user_account', key: 'user' },
          { title: '设备', dataIndex: 'device_hostname', key: 'device' },
          { title: '站点', dataIndex: 'user_site', key: 'site' },
          { title: '隧道类型', dataIndex: 'tunnel_type', key: 'tunnel', render: (v: string) => <Tag color={tunnelColor(v)}>{v}</Tag> },
          { title: '认证方式', dataIndex: 'auth_method', key: 'auth' },
          { title: '连接时间', dataIndex: 'connection_time', key: 'time', width: 180 },
          { title: '入站', dataIndex: 'bytes_in', key: 'in', render: (v: number) => v > 0 ? `${(v / 1024 / 1024).toFixed(1)} MB` : '-' },
          { title: '出站', dataIndex: 'bytes_out', key: 'out', render: (v: number) => v > 0 ? `${(v / 1024 / 1024).toFixed(1)} MB` : '-' },
        ]} rowKey="session_id" size="small" />
      </Card>

      <Card title="Always On VPN策略" style={{ marginTop: 16 }}>
        <Table dataSource={policies} columns={[
          { title: '策略名称', dataIndex: 'policy_name', key: 'name' },
          { title: '类型', dataIndex: 'policy_type', key: 'type', render: (v: string) => <Tag color="blue">{v}</Tag> },
          { title: '状态', dataIndex: 'is_enabled', key: 'enabled', render: (v: boolean) => v ? <Tag color="green">启用</Tag> : <Tag color="red">禁用</Tag> },
          { title: '配置', dataIndex: 'policy_config', key: 'config', render: (v: Record<string, unknown>) => <span style={{ fontSize: 12 }}>{JSON.stringify(v).substring(0, 80)}...</span> },
        ]} rowKey="policy_id" size="small" pagination={false} />
      </Card>

      <Card title="VPN审计日志" style={{ marginTop: 16 }}>
        <Table dataSource={auditLogs} columns={[
          { title: '事件类型', dataIndex: 'event_type', key: 'type', render: (v: string) => <Tag>{v}</Tag> },
          { title: '用户', dataIndex: 'user_account', key: 'user' },
          { title: '站点', dataIndex: 'source_site', key: 'site' },
          { title: '时间', dataIndex: 'event_time', key: 'time', width: 180 },
        ]} rowKey="log_id" size="small" pagination={{ pageSize: 10 }} />
      </Card>
    </div>
  )
}