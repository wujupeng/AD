import { Card, Table, Tag, Button, Modal, Form, Input, Select, message } from 'antd'
import { useEffect, useState } from 'react'
import client from '../../api/client'

interface SamlOidcApp {
  app_id: string
  app_name: string
  protocol: string
  entity_id: string
  callback_url: string
  is_enabled: boolean
  created_at: string
}

export default function SamlOidcAppManager() {
  const [apps, setApps] = useState<SamlOidcApp[]>([])
  const [modalOpen, setModalOpen] = useState(false)
  const [form] = Form.useForm()

  const fetchApps = async () => {
    try { const { data } = await client.get('/v1/enterprise/identity/saml-oidc-apps'); if (data.code === 0) setApps(data.data || []) } catch {}
  }

  useEffect(() => { fetchApps() }, [])

  const handleAdd = async (values: any) => {
    try {
      await client.post('/v1/enterprise/identity/saml-oidc-apps', values)
      message.success('应用注册成功')
      setModalOpen(false)
      form.resetFields()
      fetchApps()
    } catch { message.error('注册失败') }
  }

  const handleDelete = async (appId: string) => {
    try {
      await client.delete(`/v1/enterprise/identity/saml-oidc-apps/${appId}`)
      message.success('应用已删除')
      fetchApps()
    } catch { message.error('删除失败') }
  }

  return (
    <Card title="SAML/OIDC应用管理" extra={<Button type="primary" size="small" onClick={() => setModalOpen(true)}>注册应用</Button>}>
      <Table dataSource={apps} columns={[
        { title: '应用名称', dataIndex: 'app_name', key: 'name' },
        { title: '协议', dataIndex: 'protocol', key: 'proto', render: (v: string) => <Tag color={v === 'SAML' ? 'blue' : 'green'}>{v}</Tag> },
        { title: 'Entity ID', dataIndex: 'entity_id', key: 'eid', ellipsis: true },
        { title: '回调URL', dataIndex: 'callback_url', key: 'cb', ellipsis: true },
        { title: '状态', dataIndex: 'is_enabled', key: 'enabled', render: (v: boolean) => <Tag color={v ? 'green' : 'red'}>{v ? '启用' : '禁用'}</Tag> },
        {
          title: '操作', key: 'action', render: (_: any, r: SamlOidcApp) => (
            <Button size="small" danger onClick={() => handleDelete(r.app_id)}>删除</Button>
          ),
        },
      ]} rowKey="app_id" size="small" pagination={{ pageSize: 5 }} />

      <Modal title="注册SAML/OIDC应用" open={modalOpen} onCancel={() => setModalOpen(false)} onOk={() => form.submit()}>
        <Form form={form} layout="vertical" onFinish={handleAdd}>
          <Form.Item name="app_name" label="应用名称" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="protocol" label="协议" rules={[{ required: true }]}>
            <Select options={[{ value: 'SAML', label: 'SAML 2.0' }, { value: 'OIDC', label: 'OpenID Connect' }]} />
          </Form.Item>
          <Form.Item name="entity_id" label="Entity ID" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="callback_url" label="回调URL" rules={[{ required: true }]}><Input /></Form.Item>
        </Form>
      </Modal>
    </Card>
  )
}