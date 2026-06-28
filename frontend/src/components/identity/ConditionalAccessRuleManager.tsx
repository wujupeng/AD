import { Card, Table, Tag, Button, Modal, Form, Input, Select, message } from 'antd'
import { useEffect, useState } from 'react'
import client from '../../api/client'

interface ConditionalAccessRule {
  rule_id: string
  rule_name: string
  condition_type: string
  target_resources: string[]
  access_action: string
  is_enabled: boolean
  created_at: string
}

export default function ConditionalAccessRuleManager() {
  const [rules, setRules] = useState<ConditionalAccessRule[]>([])
  const [modalOpen, setModalOpen] = useState(false)
  const [form] = Form.useForm()

  const fetchRules = async () => {
    try { const { data } = await client.get('/v1/enterprise/identity/conditional-access-rules'); if (data.code === 0) setRules(data.data || []) } catch {}
  }

  useEffect(() => { fetchRules() }, [])

  const handleAdd = async (values: any) => {
    try {
      const payload = { ...values, target_resources: values.target_resources ? values.target_resources.split(',').map((s: string) => s.trim()) : [] }
      await client.post('/v1/enterprise/identity/conditional-access-rules', payload)
      message.success('条件访问规则创建成功')
      setModalOpen(false)
      form.resetFields()
      fetchRules()
    } catch { message.error('创建失败') }
  }

  const actionColor = (a: string) => {
    const m: Record<string, string> = { allow: 'green', block: 'red', mfa_required: 'orange' }
    return m[a] || 'default'
  }
  const actionLabel = (a: string) => {
    const m: Record<string, string> = { allow: '允许', block: '阻止', mfa_required: '要求MFA' }
    return m[a] || a
  }

  return (
    <Card title="条件访问规则" extra={<Button type="primary" size="small" onClick={() => setModalOpen(true)}>新建规则</Button>}>
      <Table dataSource={rules} columns={[
        { title: '规则名称', dataIndex: 'rule_name', key: 'name' },
        { title: '条件类型', dataIndex: 'condition_type', key: 'cond', render: (v: string) => <Tag>{v}</Tag> },
        { title: '目标资源', dataIndex: 'target_resources', key: 'res', render: (v: string[]) => v?.map(r => <Tag key={r} color="blue">{r}</Tag>) },
        { title: '动作', dataIndex: 'access_action', key: 'action', render: (v: string) => <Tag color={actionColor(v)}>{actionLabel(v)}</Tag> },
        { title: '状态', dataIndex: 'is_enabled', key: 'enabled', render: (v: boolean) => <Tag color={v ? 'green' : 'red'}>{v ? '启用' : '禁用'}</Tag> },
      ]} rowKey="rule_id" size="small" pagination={{ pageSize: 5 }} />

      <Modal title="新建条件访问规则" open={modalOpen} onCancel={() => setModalOpen(false)} onOk={() => form.submit()}>
        <Form form={form} layout="vertical" onFinish={handleAdd}>
          <Form.Item name="rule_name" label="规则名称" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="condition_type" label="条件类型" rules={[{ required: true }]}>
            <Select options={[
              { value: 'location', label: '位置' },
              { value: 'device_compliance', label: '设备合规' },
              { value: 'user_risk', label: '用户风险' },
              { value: 'sign_in_risk', label: '登录风险' },
              { value: 'application', label: '应用程序' },
            ]} />
          </Form.Item>
          <Form.Item name="target_resources" label="目标资源(逗号分隔)"><Input placeholder="SharePoint,Exchange,O365" /></Form.Item>
          <Form.Item name="access_action" label="访问动作" rules={[{ required: true }]}>
            <Select options={[
              { value: 'allow', label: '允许' },
              { value: 'block', label: '阻止' },
              { value: 'mfa_required', label: '要求MFA' },
            ]} />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  )
}