import { Tabs, Card, Descriptions, Tag, Switch, InputNumber, Button, message, Table, Modal, Form, Input, Select, Alert, Statistic, Row, Col, Popconfirm, Space } from 'antd'
import { useEffect, useState } from 'react'
import client from '../api/client'

interface CachedCredPolicy {
  policy_id: string
  policy_name: string
  policy_config: { enterprise_laptop: number; enterprise_desktop: number; byod: number; kiosk: number }
  is_enabled: boolean
  version: number
}

interface HybridJoinStatus {
  status: string
  total_devices: number
  registered: number
  pending: number
  failed: number
  message: string
}

interface DcIsolationPolicyData {
  policy_id: string
  isolation_enabled: boolean
  rules: any[]
  message: string
  version: number
}

interface SiteData {
  site_code: string
  site_name: string
  site_display_name: string | null
  region: string | null
  is_active: boolean
  dc_priority_list: any
  dfs_servers: string[] | null
  print_servers: string[] | null
  vpn_gateway: string | null
}

function CachedCredTab() {
  const [policy, setPolicy] = useState<CachedCredPolicy | null>(null)
  const [config, setConfig] = useState<any>({})
  const [enabled, setEnabled] = useState(true)

  const fetchPolicy = async () => {
    try { const { data } = await client.get('/v1/enterprise/settings/cached-cred-policy'); if (data.code === 0) { setPolicy(data.data); setConfig(data.data.policy_config); setEnabled(data.data.is_enabled) } } catch {}
  }
  useEffect(() => { fetchPolicy() }, [])

  const handleSave = async () => {
    if (!policy) return
    if (config.byod !== 0 || config.kiosk !== 0) { message.error('BYOD和Kiosk设备禁止缓存域凭据'); return }
    if (config.enterprise_laptop < 1 || config.enterprise_laptop > 500) { message.error('企业笔记本缓存次数范围1-500'); return }
    if (config.enterprise_desktop < 1 || config.enterprise_desktop > 50) { message.error('企业台式机缓存次数范围1-50'); return }
    try {
      await client.put('/v1/enterprise/settings/cached-cred-policy', { policy_config: config, is_enabled: enabled, version: policy.version })
      message.success('策略已更新')
      fetchPolicy()
    } catch { message.error('更新失败') }
  }

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <span>策略启用：</span>
        <Switch checked={enabled} onChange={setEnabled} />
      </div>
      <Table dataSource={[
        { key: 'enterprise_laptop', label: '企业笔记本', value: config.enterprise_laptop, editable: true, desc: '范围1-500' },
        { key: 'enterprise_desktop', label: '企业台式机', value: config.enterprise_desktop, editable: true, desc: '范围1-50' },
        { key: 'byod', label: 'BYOD', value: 0, editable: false, desc: '禁止缓存域凭据' },
        { key: 'kiosk', label: 'Kiosk终端', value: 0, editable: false, desc: '禁止缓存域凭据' },
      ]} columns={[
        { title: '终端分类', dataIndex: 'label', key: 'label' },
        { title: '缓存次数', dataIndex: 'value', key: 'value', render: (_: number, r: any) =>
          r.editable ? <InputNumber min={1} max={r.key === 'enterprise_laptop' ? 500 : 50} value={config[r.key]} onChange={val => setConfig({ ...config, [r.key]: val })} /> : <Tag color="red">0 (禁止)</Tag>
        },
        { title: '说明', dataIndex: 'desc', key: 'desc' },
      ]} pagination={false} size="small" />
      <Button type="primary" style={{ marginTop: 16 }} onClick={handleSave}>保存</Button>
    </div>
  )
}

function HybridJoinTab() {
  const [status, setStatus] = useState<HybridJoinStatus | null>(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [form] = Form.useForm()

  const fetchStatus = async () => {
    try { const { data } = await client.get('/v1/enterprise/settings/hybrid-join'); if (data.code === 0) setStatus(data.data) } catch {}
  }
  useEffect(() => { fetchStatus() }, [])
  useEffect(() => { fetchStatus() }, [])

  const handleConfigure = async (values: any) => {
    try {
      await client.post('/v1/enterprise/settings/hybrid-join/configure', values)
      message.success('配置已提交')
      setModalOpen(false)
      fetchStatus()
    } catch { message.error('配置失败') }
  }


  return (
    <div>
      {status?.message && <Alert message={status.message} type="info" style={{ marginBottom: 16 }} showIcon />}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}><Statistic title="状态" value={status?.status || '-'} valueStyle={{ fontSize: 14 }} /></Col>
        <Col span={6}><Statistic title="总设备" value={status?.total_devices || 0} /></Col>
        <Col span={6}><Statistic title="已注册" value={status?.registered || 0} valueStyle={{ color: '#3f8600' }} /></Col>
        <Col span={6}><Statistic title="失败" value={status?.failed || 0} valueStyle={{ color: '#cf1322' }} /></Col>
      </Row>
      <Button type="primary" onClick={() => setModalOpen(true)} disabled={status?.status === 'not_configured'}>配置Entra Hybrid Join</Button>
      {status?.status === 'not_configured' && <span style={{ marginLeft: 8, color: '#999' }}>需要Phase2+才可配置</span>}
      <Modal title="配置Entra Hybrid Join" open={modalOpen} onCancel={() => setModalOpen(false)} onOk={() => form.submit()}>
        <Form form={form} layout="vertical" onFinish={handleConfigure}>
          <Form.Item name="entra_connect_server" label="Entra Connect服务器"><Input /></Form.Item>
          <Form.Item name="sync_scope" label="同步范围"><Select options={[{ value: 'all', label: '全部' }, { value: 'selected_ous', label: '选定OU' }]} /></Form.Item>
          <Form.Item name="device_registration_policy" label="设备注册策略"><Input /></Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

function DcIsolationTab() {
  const [policy, setPolicy] = useState<DcIsolationPolicyData | null>(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [form] = Form.useForm()

  const fetchPolicy = async () => {
    try { const { data } = await client.get('/v1/enterprise/settings/dc-isolation'); if (data.code === 0) setPolicy(data.data) } catch {}
  }
  useEffect(() => { fetchPolicy() }, [])

  const handleToggle = async (enabled: boolean) => {
    if (!policy) return
    try {
      await client.put('/v1/enterprise/settings/dc-isolation', { isolation_enabled: enabled, version: policy.version })
      fetchPolicy()
    } catch { message.error('更新失败') }
  }

  const handleAddRule = async (values: any) => {
    if (!policy) return
    const newRule = { ...values, rule_id: crypto.randomUUID(), is_enabled: true, is_default: false }
    const rules = [...(policy.rules || []), newRule]
    try {
      await client.put('/v1/enterprise/settings/dc-isolation', { rules, version: policy.version })
      message.success('规则已添加')
      setModalOpen(false)
      fetchPolicy()
    } catch { message.error('添加失败') }
  }

  const handleToggleRule = async (ruleId: string, enabled: boolean) => {
    if (!policy) return
    const rules = (policy.rules || []).map((r: any) => r.rule_id === ruleId ? { ...r, is_enabled: enabled } : r)
    try {
      await client.put('/v1/enterprise/settings/dc-isolation', { rules, version: policy.version })
      fetchPolicy()
    } catch { message.error('更新失败') }
  }

  return (
    <div>
      {policy?.message && <Alert message={policy.message} type="warning" style={{ marginBottom: 16 }} showIcon />}
      <Space style={{ marginBottom: 16 }}>
        <span>隔离策略：</span>
        <Popconfirm title="禁用域控安全隔离将暴露DC到不受控的网络访问，确认禁用？" onConfirm={() => handleToggle(false)} okText="确认" cancelText="取消">
          <Switch checked={policy?.isolation_enabled ?? true} onChange={checked => { if (checked) handleToggle(true) }} />
        </Popconfirm>
        <Button type="primary" size="small" onClick={() => setModalOpen(true)}>添加规则</Button>
      </Space>
      <Table dataSource={policy?.rules || []} columns={[
        { title: '规则名称', dataIndex: 'rule_name', key: 'name' },
        { title: '方向', dataIndex: 'direction', key: 'dir' },
        { title: '源地址', dataIndex: 'source_address', key: 'src' },
        { title: '目标端口', dataIndex: 'destination_port', key: 'port' },
        { title: '协议', dataIndex: 'protocol', key: 'proto' },
        { title: '动作', dataIndex: 'action', key: 'action', render: (v: string) => <Tag color={v === 'allow' ? 'green' : 'red'}>{v === 'allow' ? '允许' : '拒绝'}</Tag> },
        { title: '启用', dataIndex: 'is_enabled', key: 'enabled', render: (v: boolean, r: any) => <Switch size="small" checked={v} onChange={checked => handleToggleRule(r.rule_id, checked)} /> },
        { title: '默认', dataIndex: 'is_default', key: 'default', render: (v: boolean) => v ? <Tag>默认</Tag> : '-' },
      ]} rowKey="rule_id" size="small" pagination={false} />

      <Modal title="添加隔离规则" open={modalOpen} onCancel={() => setModalOpen(false)} onOk={() => form.submit()}>
        <Form form={form} layout="vertical" onFinish={handleAddRule}>
          <Form.Item name="rule_name" label="规则名称" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="direction" label="方向" rules={[{ required: true }]}><Select options={[{ value: 'inbound', label: '入站' }, { value: 'outbound', label: '出站' }]} /></Form.Item>
          <Form.Item name="source_address" label="源地址(CIDR)" rules={[{ required: true }]}><Input placeholder="10.0.0.0/8" /></Form.Item>
          <Form.Item name="destination_port" label="目标端口" rules={[{ required: true }]}><Input placeholder="389,636,88,53" /></Form.Item>
          <Form.Item name="protocol" label="协议" rules={[{ required: true }]}><Select options={[{ value: 'TCP', label: 'TCP' }, { value: 'UDP', label: 'UDP' }, { value: 'TCP/UDP', label: 'TCP/UDP' }]} /></Form.Item>
          <Form.Item name="action" label="动作" rules={[{ required: true }]}><Select options={[{ value: 'allow', label: '允许' }, { value: 'deny', label: '拒绝' }]} /></Form.Item>
          <Form.Item name="priority" label="优先级" initialValue={500}><InputNumber min={1} max={9999} style={{ width: '100%' }} /></Form.Item>
          <Form.Item name="description" label="描述"><Input /></Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

function SiteConfigTab() {
  const [sites, setSites] = useState<SiteData[]>([])
  const [selectedSite, setSelectedSite] = useState<string | null>(null)

  const fetchSites = async () => {
    try { const { data } = await client.get('/v1/enterprise/settings/sites'); if (data.code === 0) setSites(data.data || []) } catch {}
  }
  useEffect(() => { fetchSites() }, [])

  const site = sites.find(s => s.site_code === selectedSite)

  return (
    <Row gutter={16}>
      <Col span={8}>
        <Card title="站点列表" size="small">
          {sites.map(s => (
            <div key={s.site_code} style={{ padding: '8px 12px', cursor: 'pointer', background: selectedSite === s.site_code ? '#e6f7ff' : undefined, borderRadius: 4, marginBottom: 4 }} onClick={() => setSelectedSite(s.site_code)}>
              <span>{s.site_display_name || s.site_name}</span>
              <Tag color={s.is_active ? 'green' : 'red'} style={{ marginLeft: 8 }}>{s.is_active ? '活跃' : '停用'}</Tag>
            </div>
          ))}
        </Card>
      </Col>
      <Col span={16}>
        {site ? (
          <Card title={`${site.site_display_name || site.site_name} 配置`} size="small">
            <Descriptions column={1} bordered size="small">
              <Descriptions.Item label="站点代码">{site.site_code}</Descriptions.Item>
              <Descriptions.Item label="区域">{site.region || '-'}</Descriptions.Item>
              <Descriptions.Item label="DC列表">{site.dc_priority_list ? JSON.stringify(site.dc_priority_list) : '-'}</Descriptions.Item>
              <Descriptions.Item label="DFS服务器">{site.dfs_servers?.map(s => <Tag key={s}>{s}</Tag>) || '-'}</Descriptions.Item>
              <Descriptions.Item label="打印服务器">{site.print_servers?.map(s => <Tag key={s}>{s}</Tag>) || '-'}</Descriptions.Item>
              <Descriptions.Item label="VPN网关">{site.vpn_gateway || '-'}</Descriptions.Item>
              <Descriptions.Item label="状态"><Tag color={site.is_active ? 'green' : 'red'}>{site.is_active ? '活跃' : '停用'}</Tag></Descriptions.Item>
            </Descriptions>
          </Card>
        ) : <Card><span style={{ color: '#999' }}>请选择站点</span></Card>}
      </Col>
    </Row>
  )
}

function IntegrationConfigTab() {
  const [ldapConfigs, setLdapConfigs] = useState<any[]>([])
  const [externalIntegrations, setExternalIntegrations] = useState<any[]>([])

  const fetchLdap = async () => {
    try { const { data } = await client.get('/v1/enterprise/settings/integrations/ldap'); if (data.code === 0) setLdapConfigs(data.data || []) } catch {}
  }
  const fetchExternal = async () => {
    try { const { data } = await client.get('/v1/enterprise/settings/integrations/external'); if (data.code === 0) setExternalIntegrations(data.data || []) } catch {}
  }

  useEffect(() => { fetchLdap(); fetchExternal() }, [])

  return (
    <Tabs items={[
      { key: 'ldap', label: 'LDAP目录', children: (
        <Table dataSource={ldapConfigs} columns={[
          { title: '名称', dataIndex: 'config_name', key: 'name' },
          { title: '服务器', dataIndex: 'server_url', key: 'url' },
          { title: 'Base DN', dataIndex: 'base_dn', key: 'dn' },
          { title: '状态', dataIndex: 'connection_test_status', key: 'status', render: (v: string) => <Tag color={v === 'success' ? 'green' : v === 'failed' ? 'red' : 'default'}>{v}</Tag> },
        ]} rowKey="config_id" size="small" />
      )},
      { key: 'external', label: '外部集成', children: (
        <Table dataSource={externalIntegrations} columns={[
          { title: '名称', dataIndex: 'integration_name', key: 'name' },
          { title: '类型', dataIndex: 'integration_type', key: 'type', render: (v: string) => <Tag color="blue">{v}</Tag> },
          { title: '服务器', dataIndex: 'server_url', key: 'url' },
          { title: '状态', dataIndex: 'connection_status', key: 'status', render: (v: string) => <Tag color={v === 'connected' ? 'green' : v === 'error' ? 'red' : 'default'}>{v}</Tag> },
        ]} rowKey="integration_id" size="small" />
      )},
    ]} />
  )
}

export default function SettingsPage() {
  return (
    <Card title="系统配置">
      <Tabs items={[
        { key: 'cached-cred', label: '缓存域凭据', children: <CachedCredTab /> },
        { key: 'hybrid-join', label: 'Entra Hybrid Join', children: <HybridJoinTab /> },
        { key: 'dc-isolation', label: '域控安全隔离', children: <DcIsolationTab /> },
        { key: 'sites', label: '站点配置', children: <SiteConfigTab /> },
        { key: 'integrations', label: '集成配置', children: <IntegrationConfigTab /> },
      ]} />
    </Card>
  )
}