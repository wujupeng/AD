import { Card, Table, Tag, Button, Modal, Form, Input, Select, Space, DatePicker, message, Steps, Descriptions } from 'antd'
import { useEffect, useState } from 'react'
import client from '../api/client'

interface OffboardingRequest {
  request_id: string
  ad_account: string
  offboarding_date: string
  mailbox_retention_days: number
  mailbox_forward_to: string | null
  wipe_device: boolean
  revoke_all_access: boolean
  status: string
  created_at: string
}

export default function HrOffboardingPage() {
  const [requests, setRequests] = useState<OffboardingRequest[]>([])
  const [modalOpen, setModalOpen] = useState(false)
  const [detailReq, setDetailReq] = useState<OffboardingRequest | null>(null)
  const [form] = Form.useForm()

  const fetchRequests = async () => {
    try { const { data } = await client.get('/v1/enterprise/identity/offboarding?limit=50'); if (data.code === 0) setRequests(data.data || []) } catch {}
  }

  useEffect(() => { fetchRequests() }, [])

  const handleSubmit = async (values: any) => {
    try {
      const payload = { ...values, offboarding_date: values.offboarding_date?.format('YYYY-MM-DDTHH:mm:ssZ') }
      await client.post('/v1/enterprise/identity/offboarding', payload)
      message.success('离职请求已创建')
      setModalOpen(false)
      form.resetFields()
      fetchRequests()
    } catch { message.error('创建失败') }
  }

  const fetchDetail = async (requestId: string) => {
    try {
      const { data } = await client.get(`/v1/enterprise/identity/offboarding/${requestId}`)
      if (data.code === 0) setDetailReq(data.data)
    } catch {}
  }

  const statusColor = (s: string) => {
    const m: Record<string, string> = { pending: 'blue', in_progress: 'orange', completed: 'green', partial_failed: 'volcano', failed: 'red' }
    return m[s] || 'default'
  }
  const statusLabel = (s: string) => {
    const m: Record<string, string> = { pending: '待处理', in_progress: '处理中', completed: '已完成', partial_failed: '部分失败', failed: '失败' }
    return m[s] || s
  }

  return (
    <div>
      <Card title="HR离职管理" extra={<Button type="primary" onClick={() => setModalOpen(true)}>新建离职请求</Button>}>
        <Table dataSource={requests} columns={[
          { title: '请求ID', dataIndex: 'request_id', key: 'id', render: (v: string) => v?.substring(0, 8) + '...' },
          { title: 'AD账号', dataIndex: 'ad_account', key: 'ad' },
          { title: '离职日期', dataIndex: 'offboarding_date', key: 'date' },
          { title: '邮箱保留天数', dataIndex: 'mailbox_retention_days', key: 'retention' },
          { title: '状态', dataIndex: 'status', key: 'status', render: (v: string) => <Tag color={statusColor(v)}>{statusLabel(v)}</Tag> },
          {
            title: '操作', key: 'action', render: (_: any, r: OffboardingRequest) => (
              <Space>
                <Button size="small" onClick={() => fetchDetail(r.request_id)}>详情</Button>
                {(r.status === 'pending' || r.status === 'partial_failed') && (
                  <Button size="small" type="primary" danger onClick={async () => { try { await client.post(`/v1/enterprise/identity/offboarding/${r.request_id}/execute`); message.success('离职执行成功'); fetchRequests() } catch { message.error('执行失败') } }}>执行离职</Button>
                )}
              </Space>
            ),
          },
        ]} rowKey="request_id" size="small" />
      </Card>

      <Modal title="新建离职请求" open={modalOpen} onCancel={() => setModalOpen(false)} onOk={() => form.submit()} width={600}>
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item name="ad_account" label="AD账号" rules={[{ required: true }]}><Input placeholder="zhangsan@company.local" /></Form.Item>
          <Form.Item name="offboarding_date" label="离职日期" rules={[{ required: true }]}><DatePicker showTime style={{ width: '100%' }} /></Form.Item>
          <Form.Item name="mailbox_retention_days" label="邮箱保留天数" initialValue={30}><Input type="number" /></Form.Item>
          <Form.Item name="mailbox_forward_to" label="邮箱转发至"><Input placeholder="可选" /></Form.Item>
          <Form.Item name="wipe_device" label="擦除设备" valuePropName="checked" initialValue={true}><Select options={[{ value: true, label: '是' }, { value: false, label: '否' }]} /></Form.Item>
          <Form.Item name="revoke_all_access" label="撤销所有访问" valuePropName="checked" initialValue={true}><Select options={[{ value: true, label: '是' }, { value: false, label: '否' }]} /></Form.Item>
        </Form>
      </Modal>

      <Modal title="离职请求详情" open={!!detailReq} onCancel={() => setDetailReq(null)} footer={null} width={700}>
        {detailReq && (
          <div>
            <Steps current={detailReq.status === 'completed' ? 2 : detailReq.status === 'in_progress' ? 1 : 0}
              items={[{ title: '提交' }, { title: '处理中' }, { title: '完成' }]} style={{ marginBottom: 24 }} />
            <Descriptions column={2} bordered size="small">
              <Descriptions.Item label="请求ID">{detailReq.request_id}</Descriptions.Item>
              <Descriptions.Item label="AD账号">{detailReq.ad_account}</Descriptions.Item>
              <Descriptions.Item label="离职日期">{detailReq.offboarding_date}</Descriptions.Item>
              <Descriptions.Item label="邮箱保留天数">{detailReq.mailbox_retention_days}</Descriptions.Item>
              <Descriptions.Item label="邮箱转发">{detailReq.mailbox_forward_to || '-'}</Descriptions.Item>
              <Descriptions.Item label="擦除设备">{detailReq.wipe_device ? '是' : '否'}</Descriptions.Item>
              <Descriptions.Item label="撤销所有访问">{detailReq.revoke_all_access ? '是' : '否'}</Descriptions.Item>
              <Descriptions.Item label="状态"><Tag color={statusColor(detailReq.status)}>{statusLabel(detailReq.status)}</Tag></Descriptions.Item>
            </Descriptions>
          </div>
        )}
      </Modal>
    </div>
  )
}
