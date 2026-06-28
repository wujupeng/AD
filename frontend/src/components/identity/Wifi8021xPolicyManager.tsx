import { Card, Table, Tag, Button, Modal, Form, Input, Select, message } from 'antd'
import { useEffect, useState } from 'react'
import client from '../../api/client'

interface WifiPolicy {
  policy_id: string
  policy_name: string
  ssid: string
  auth_method: string
  certificate_template: string | null
  is_enabled: boolean
  created_at: string
}

export default function Wifi8021xPolicyManager() {
  const [policies, setPolicies] = useState<WifiPolicy[]>([])
  const [modalOpen, setModalOpen] = useState(false)
  const [form] = Form.useForm()

  const fetchPolicies = async () => {
    try { const { data } = await client.get('/v1/enterprise/identity/wifi-8021x-policies'); if (data.code === 0) setPolicies(data.data || []) } catch {}
  }

  useEffect(() => { fetchPolicies() }, [])

  const handleAdd = async (values: any) => {
    try {
      await client.post('/v1/enterprise/identity/wifi-8021x-policies', values)
      message.success('Wi-Fi策略创建成功')
      setModalOpen(false)
      form.resetFields()
      fetchPolicies()
    } catch { message.error('创建失败') }
  }

  return (
    <Card title="Wi-Fi 802.1X策略" extra={<Button type="primary" size="small" onClick={() => setModalOpen(true)}>新建策略</Button>}>
      <Table dataSource={policies} columns={[
        { title: '策略名称', dataIndex: 'policy_name', key: 'name' },
        { title: 'SSID', dataIndex: 'ssid', key: 'ssid' },
        { title: '认证方式', dataIndex: 'auth_method', key: 'auth', render: (v: string) => <Tag color="blue">{v}</Tag> },
        { title: '证书模板', dataIndex: 'certificate_template', key: 'cert', render: (v: string | null) => v || '-' },
        { title: '状态', dataIndex: 'is_enabled', key: 'enabled', render: (v: boolean) => <Tag color={v ? 'green' : 'red'}>{v ? '启用' : '禁用'}</Tag> },
      ]} rowKey="policy_id" size="small" pagination={{ pageSize: 5 }} />

      <Modal title="新建Wi-Fi 802.1X策略" open={modalOpen} onCancel={() => setModalOpen(false)} onOk={() => form.submit()}>
        <Form form={form} layout="vertical" onFinish={handleAdd}>
          <Form.Item name="policy_name" label="策略名称" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="ssid" label="SSID" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="auth_method" label="认证方式" rules={[{ required: true }]}>
            <Select options={[
              { value: 'EAP-TLS', label: 'EAP-TLS (证书)' },
              { value: 'PEAP-MSCHAPv2', label: 'PEAP-MSCHAPv2' },
              { value: 'EAP-TTLS', label: 'EAP-TTLS' },
            ]} />
          </Form.Item>
          <Form.Item name="certificate_template" label="证书模板"><Input placeholder="可选" /></Form.Item>
        </Form>
      </Modal>
    </Card>
  )
}