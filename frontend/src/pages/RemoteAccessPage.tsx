import { Card, Table, Tag, Descriptions, Row, Col } from 'antd'
import { useEffect, useState } from 'react'
import client from '../api/client'

interface VpnGateway {
  gateway_id: string
  gateway_name: string
  gateway_site: string
  gateway_ip: string
  gateway_role: string
  tunnel_protocol: string
  max_concurrent_sessions: number
  active_sessions: number
  cpu_usage_percent: number
  bandwidth_usage_mbps: number
  health_status: string
  served_sites: string[]
}

interface DeviceClassification {
  device_class: string
  display_name: string
  auth_methods: string[]
  vpn_tunnel_type: string | null
  cached_logon_count: number
  conditional_access_level: string
  bitlocker_required: boolean
  defender_required: boolean
}

export default function RemoteAccessPage() {
  const [gateways, setGateways] = useState<VpnGateway[]>([])
  const [classifications, setClassifications] = useState<DeviceClassification[]>([])
  const [cachedCredPolicy, setCachedCredPolicy] = useState<Record<string, unknown> | null>(null)
  const [hybridJoinStatus, setHybridJoinStatus] = useState<Record<string, unknown> | null>(null)
  const [dcIsolation, setDcIsolation] = useState<Record<string, unknown> | null>(null)

  const fetchGateways = async () => {
    try { const { data } = await client.get('/v1/enterprise/vpn/gateways'); if (data.code === 0) setGateways(data.data) } catch {}
  }
  const fetchClassifications = async () => {
    try { const { data } = await client.get('/v1/enterprise/remote-access/device-classification'); if (data.code === 0) setClassifications(data.data) } catch {}
  }
  const fetchCachedCred = async () => {
    try { const { data } = await client.get('/v1/enterprise/remote-access/cached-cred-policy'); if (data.code === 0) setCachedCredPolicy(data.data) } catch {}
  }
  const fetchHybridJoin = async () => {
    try { const { data } = await client.get('/v1/enterprise/remote-access/hybrid-join-status'); if (data.code === 0) setHybridJoinStatus(data.data) } catch {}
  }
  const fetchDcIsolation = async () => {
    try { const { data } = await client.get('/v1/enterprise/remote-access/dc-isolation'); if (data.code === 0) setDcIsolation(data.data) } catch {}
  }

  useEffect(() => { fetchGateways(); fetchClassifications(); fetchCachedCred(); fetchHybridJoin(); fetchDcIsolation() }, [])

  const healthColor = (s: string) => s === 'online' ? 'green' : s === 'degraded' ? 'orange' : s === 'offline' ? 'red' : 'default'
  const caColor = (l: string) => l === 'strict' ? 'red' : l === 'enhanced' ? 'orange' : 'green'

  return (
    <div>
      <Card title="VPN网关状态" style={{ marginBottom: 16 }}>
        <Row gutter={[16, 16]}>
          {gateways.map(gw => (
            <Col span={12} key={gw.gateway_id}>
              <Card size="small" title={`${gw.gateway_name} (${gw.gateway_role === 'primary' ? '主' : '备'})`}
                extra={<Tag color={healthColor(gw.health_status)}>{gw.health_status}</Tag>}>
                <Descriptions column={2} size="small">
                  <Descriptions.Item label="站点">{gw.gateway_site}</Descriptions.Item>
                  <Descriptions.Item label="IP">{gw.gateway_ip}</Descriptions.Item>
                  <Descriptions.Item label="协议">{gw.tunnel_protocol}</Descriptions.Item>
                  <Descriptions.Item label="会话">{gw.active_sessions}/{gw.max_concurrent_sessions}</Descriptions.Item>
                  <Descriptions.Item label="CPU">{gw.cpu_usage_percent.toFixed(1)}%</Descriptions.Item>
                  <Descriptions.Item label="带宽">{gw.bandwidth_usage_mbps.toFixed(1)} Mbps</Descriptions.Item>
                </Descriptions>
                <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>服务站点: {gw.served_sites?.join(', ')}</div>
              </Card>
            </Col>
          ))}
        </Row>
      </Card>

      <Card title="终端分类认证策略" style={{ marginBottom: 16 }}>
        <Table dataSource={classifications} columns={[
          { title: '分类', dataIndex: 'display_name', key: 'name' },
          { title: '认证方式', dataIndex: 'auth_methods', key: 'auth', render: (v: string[]) => v?.map(m => <Tag key={m}>{m}</Tag>) },
          { title: 'VPN隧道', dataIndex: 'vpn_tunnel_type', key: 'tunnel' },
          { title: '缓存凭据', dataIndex: 'cached_logon_count', key: 'cache' },
          { title: '条件访问', dataIndex: 'conditional_access_level', key: 'ca', render: (v: string) => <Tag color={caColor(v)}>{v}</Tag> },
          { title: 'BitLocker', dataIndex: 'bitlocker_required', key: 'bl', render: (v: boolean) => v ? <Tag color="green">必须</Tag> : <Tag>可选</Tag> },
          { title: 'Defender', dataIndex: 'defender_required', key: 'def', render: (v: boolean) => v ? <Tag color="green">必须</Tag> : <Tag>可选</Tag> },
        ]} rowKey="device_class" size="small" pagination={false} />
      </Card>

      <Row gutter={[16, 16]}>
        <Col span={12}>
          <Card title="缓存域凭据策略" size="small">
            {cachedCredPolicy && <pre style={{ fontSize: 12, maxHeight: 200, overflow: 'auto' }}>{JSON.stringify(cachedCredPolicy, null, 2)}</pre>}
          </Card>
        </Col>
        <Col span={12}>
          <Card title="Entra Hybrid Join" size="small">
            {hybridJoinStatus && <pre style={{ fontSize: 12, maxHeight: 200, overflow: 'auto' }}>{JSON.stringify(hybridJoinStatus, null, 2)}</pre>}
          </Card>
        </Col>
      </Row>

      <Card title="域控安全隔离策略" style={{ marginTop: 16 }}>
        {dcIsolation && <pre style={{ fontSize: 12, maxHeight: 200, overflow: 'auto' }}>{JSON.stringify(dcIsolation, null, 2)}</pre>}
      </Card>
    </div>
  )
}