import { Card, Table, Tag, Button, Modal, Form, Input, Select, message } from 'antd'
import { useEffect, useState } from 'react'
import client from '../../api/client'

interface AutopilotProfile {
  profile_id: string
  profile_name: string
  deployment_mode: string
  ou_path: string | null
  device_group: string | null
  is_enabled: boolean
  created_at: string
}

export default function AutopilotProfileManager() {
  const [profiles, setProfiles] = useState<AutopilotProfile[]>([])
  const [modalOpen, setModalOpen] = useState(false)
  const [form] = Form.useForm()

  const fetchProfiles = async () => {
    try { const { data } = await client.get('/v1/enterprise/identity/autopilot-profiles'); if (data.code === 0) setProfiles(data.data || []) } catch {}
  }

  useEffect(() => { fetchProfiles() }, [])

  const handleAdd = async (values: any) => {
    try {
      await client.post('/v1/enterprise/identity/autopilot-profiles', values)
      message.success('Autopilot配置创建成功')
      setModalOpen(false)
      form.resetFields()
      fetchProfiles()
    } catch { message.error('创建失败') }
  }

  return (
    <Card title="Windows Autopilot配置" extra={<Button type="primary" size="small" onClick={() => setModalOpen(true)}>新建配置</Button>}>
      <Table dataSource={profiles} columns={[
        { title: '配置名称', dataIndex: 'profile_name', key: 'name' },
        { title: '部署模式', dataIndex: 'deployment_mode', key: 'mode', render: (v: string) => <Tag color="blue">{v}</Tag> },
        { title: 'OU路径', dataIndex: 'ou_path', key: 'ou', ellipsis: true, render: (v: string | null) => v || '-' },
        { title: '设备组', dataIndex: 'device_group', key: 'dg', render: (v: string | null) => v ? <Tag>{v}</Tag> : '-' },
        { title: '状态', dataIndex: 'is_enabled', key: 'enabled', render: (v: boolean) => <Tag color={v ? 'green' : 'red'}>{v ? '启用' : '禁用'}</Tag> },
      ]} rowKey="profile_id" size="small" pagination={{ pageSize: 5 }} />

      <Modal title="新建Autopilot配置" open={modalOpen} onCancel={() => setModalOpen(false)} onOk={() => form.submit()}>
        <Form form={form} layout="vertical" onFinish={handleAdd}>
          <Form.Item name="profile_name" label="配置名称" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="deployment_mode" label="部署模式" rules={[{ required: true }]}>
            <Select options={[
              { value: 'self_deploying', label: '自部署' },
              { value: 'user_driven', label: '用户驱动' },
              { value: 'pre_provisioned', label: '预配置' },
            ]} />
          </Form.Item>
          <Form.Item name="ou_path" label="OU路径"><Input placeholder="OU=Computers,DC=company,DC=local" /></Form.Item>
          <Form.Item name="device_group" label="设备组"><Input /></Form.Item>
        </Form>
      </Modal>
    </Card>
  )
}