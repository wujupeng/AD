import { Card, Descriptions, Tag, Button, Modal, Form, Input, Select, Switch, InputNumber, message } from 'antd'
import { useEffect, useState } from 'react'
import client from '../../api/client'

interface IdentitySourcePolicy {
  policy_id: string
  policy_name: string
  primary_source: string
  internet_extension: string
  allow_cloud_only_users: boolean
  sync_failure_threshold_hours: number
  downstream_systems: string[]
  is_enabled: boolean
  status: string
}

export default function IdentitySourcePolicyConfig() {
  const [policy, setPolicy] = useState<IdentitySourcePolicy | null>(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [form] = Form.useForm()

  const fetchPolicy = async () => {
    try { const { data } = await client.get('/v1/enterprise/identity/source-policy'); if (data.code === 0) setPolicy(data.data) } catch {}
  }

  useEffect(() => { fetchPolicy() }, [])

  const handleUpdate = async (values: any) => {
    try {
      const payload = {
        ...values,
        policy_id: policy?.policy_id,
        downstream_systems: values.downstream_systems ? values.downstream_systems.split(',').map((s: string) => s.trim()) : [],
      }
      await client.put('/v1/enterprise/identity/source-policy', payload)
      message.success('身份源策略已更新')
      setModalOpen(false)
      fetchPolicy()
    } catch { message.error('更新失败') }
  }

  const openEditModal = () => {
    if (policy) {
      form.setFieldsValue({
        policy_name: policy.policy_name,
        primary_source: policy.primary_source,
        internet_extension: policy.internet_extension,
        allow_cloud_only_users: policy.allow_cloud_only_users,
        sync_failure_threshold_hours: policy.sync_failure_threshold_hours,
        downstream_systems: policy.downstream_systems?.join(', '),
      })
    }
    setModalOpen(true)
  }

  return (
    <Card title="唯一身份源策略配置" extra={<Button type="primary" size="small" onClick={openEditModal}>编辑</Button>}>
      {policy && policy.status !== 'not_configured' ? (
        <Descriptions column={2} bordered size="small">
          <Descriptions.Item label="策略名称">{policy.policy_name}</Descriptions.Item>
          <Descriptions.Item label="主身份源"><Tag color="green">{policy.primary_source}</Tag></Descriptions.Item>
          <Descriptions.Item label="互联网扩展"><Tag color="blue">{policy.internet_extension}</Tag></Descriptions.Item>
          <Descriptions.Item label="Cloud-only用户">{policy.allow_cloud_only_users ? <Tag color="red">允许</Tag> : <Tag color="green">禁止</Tag>}</Descriptions.Item>
          <Descriptions.Item label="同步失败阈值">{policy.sync_failure_threshold_hours}小时</Descriptions.Item>
          <Descriptions.Item label="状态"><Tag color={policy.is_enabled ? 'green' : 'red'}>{policy.is_enabled ? '启用' : '禁用'}</Tag></Descriptions.Item>
          <Descriptions.Item label="受管控下游系统" span={2}>
            {policy.downstream_systems?.map(s => <Tag key={s} color="blue" style={{ margin: 2 }}>{s}</Tag>)}
          </Descriptions.Item>
        </Descriptions>
      ) : <Tag>未配置 - 点击编辑创建策略</Tag>}

      <Modal title="编辑身份源策略" open={modalOpen} onCancel={() => setModalOpen(false)} onOk={() => form.submit()} width={600}>
        <Form form={form} layout="vertical" onFinish={handleUpdate}>
          <Form.Item name="policy_name" label="策略名称" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="primary_source" label="主身份源" rules={[{ required: true }]}>
            <Select options={[{ value: 'Active Directory', label: 'Active Directory' }, { value: 'Entra ID', label: 'Entra ID' }]} />
          </Form.Item>
          <Form.Item name="internet_extension" label="互联网身份扩展">
            <Select options={[{ value: 'Entra ID', label: 'Entra ID' }, { value: 'None', label: '无' }]} />
          </Form.Item>
          <Form.Item name="allow_cloud_only_users" label="允许Cloud-only用户" valuePropName="checked"><Switch /></Form.Item>
          <Form.Item name="sync_failure_threshold_hours" label="同步失败阈值(小时)"><InputNumber min={1} max={72} style={{ width: '100%' }} /></Form.Item>
          <Form.Item name="downstream_systems" label="受管控下游系统(逗号分隔)"><Input placeholder="Exchange, SharePoint, SAP, OA" /></Form.Item>
        </Form>
      </Modal>
    </Card>
  )
}