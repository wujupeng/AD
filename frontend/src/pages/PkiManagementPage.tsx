import { Card, Table, Tag, Button, Modal, Form, Input, Select, message } from 'antd'
import { PlusOutlined } from '@ant-design/icons'
import { useEffect, useState } from 'react'
import client from '../api/client'

interface PkiTemplate {
  template_name: string
  usage_scenario: string
  key_length: number
  validity_period_days: number
  auto_enrollment: boolean
  description: string | null
}

export default function PkiManagementPage() {
  const [templates, setTemplates] = useState<PkiTemplate[]>([])
  const [expiring, setExpiring] = useState<any[]>([])
  const [modalOpen, setModalOpen] = useState(false)
  const [form] = Form.useForm()

  const fetchTemplates = async () => {
    try {
      const { data } = await client.get('/v1/enterprise/pki/templates')
      if (data.code === 0) setTemplates(data.data)
    } catch {}
  }

  const fetchExpiring = async () => {
    try {
      const { data } = await client.get('/v1/enterprise/pki/expiring?days=30')
      if (data.code === 0) setExpiring(data.data)
    } catch {}
  }

  useEffect(() => { fetchTemplates(); fetchExpiring() }, [])

  const handleCreate = async (values: any) => {
    try {
      await client.post('/v1/enterprise/pki/templates', values)
      message.success('模板创建成功')
      setModalOpen(false)
      fetchTemplates()
    } catch { message.error('创建失败') }
  }

  const tplColumns = [
    { title: '模板名称', dataIndex: 'template_name', key: 'name' },
    { title: '用途', dataIndex: 'usage_scenario', key: 'usage' },
    { title: '密钥长度', dataIndex: 'key_length', key: 'key' },
    { title: '有效期(天)', dataIndex: 'validity_period_days', key: 'validity' },
    { title: '自动注册', dataIndex: 'auto_enrollment', key: 'auto', render: (v: boolean) => v ? <Tag color="green">是</Tag> : <Tag>否</Tag> },
    { title: '描述', dataIndex: 'description', key: 'desc' },
  ]

  return (
    <div>
      <Card title="PKI 证书模板" extra={<Button icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>新建模板</Button>}>
        <Table dataSource={templates} columns={tplColumns} rowKey="template_name" pagination={false} size="small" />
      </Card>
      <Card title="即将过期证书 (30天内)" style={{ marginTop: 16 }}>
        <Table dataSource={expiring} columns={[
          { title: '主题', dataIndex: 'subject_name', key: 'subj' },
          { title: '序列号', dataIndex: 'serial_number', key: 'serial' },
          { title: '过期时间', dataIndex: 'not_after', key: 'exp' },
          { title: '模板', dataIndex: 'template_name', key: 'tpl' },
        ]} rowKey="certificate_id" pagination={false} size="small" />
      </Card>
      <Modal title="新建证书模板" open={modalOpen} onCancel={() => setModalOpen(false)} onOk={() => form.submit()}>
        <Form form={form} onFinish={handleCreate} layout="vertical">
          <Form.Item name="template_name" label="模板名称" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="usage_scenario" label="用途" rules={[{ required: true }]}><Select options={[{value:'wifi',label:'WiFi'},{value:'vpn',label:'VPN'},{value:'https',label:'HTTPS'},{value:'code_signing',label:'代码签名'},{value:'rdp',label:'RDP'}]} /></Form.Item>
          <Form.Item name="key_length" label="密钥长度" initialValue={2048}><Select options={[{value:2048,label:'2048'},{value:4096,label:'4096'}]} /></Form.Item>
          <Form.Item name="validity_period_days" label="有效期(天)" initialValue={365}><Input type="number" /></Form.Item>
          <Form.Item name="description" label="描述"><Input.TextArea /></Form.Item>
        </Form>
      </Modal>
    </div>
  )
}