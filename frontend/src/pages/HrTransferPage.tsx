import { Card, Table, Tag, Button, Modal, Form, Input, Select, message, Steps, Descriptions } from 'antd'
import { useEffect, useState } from 'react'
import client from '../api/client'

interface TransferRequest {
  request_id: string
  ad_account: string
  old_department: string
  new_department: string
  old_site: string
  new_site: string
  new_position: string | null
  status: string
  created_at: string
}

export default function HrTransferPage() {
  const [requests, setRequests] = useState<TransferRequest[]>([])
  const [modalOpen, setModalOpen] = useState(false)
  const [detailReq, setDetailReq] = useState<TransferRequest | null>(null)
  const [form] = Form.useForm()

  const fetchRequests = async () => {
    try { const { data } = await client.get('/v1/enterprise/identity/transfer?limit=50'); if (data.code === 0) setRequests(data.data || []) } catch {}
  }

  useEffect(() => { fetchRequests() }, [])

  const handleSubmit = async (values: any) => {
    try {
      await client.post('/v1/enterprise/identity/transfer', values)
      message.success('调岗请求已创建')
      setModalOpen(false)
      form.resetFields()
      fetchRequests()
    } catch { message.error('创建失败') }
  }

  const fetchDetail = async (requestId: string) => {
    try {
      const { data } = await client.get(`/v1/enterprise/identity/transfer/${requestId}`)
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

  const siteOptions = [
    { value: 'HeadOffice', label: '总部' },
    { value: 'FactoryCN', label: '中国工厂' },
    { value: 'FactoryMX', label: '墨西哥工厂' },
    { value: 'FactoryVN', label: '越南工厂' },
    { value: 'FactoryHU', label: '匈牙利工厂' },
  ]

  return (
    <div>
      <Card title="HR调岗管理" extra={<Button type="primary" onClick={() => setModalOpen(true)}>新建调岗请求</Button>}>
        <Table dataSource={requests} columns={[
          { title: '请求ID', dataIndex: 'request_id', key: 'id', render: (v: string) => v?.substring(0, 8) + '...' },
          { title: 'AD账号', dataIndex: 'ad_account', key: 'ad' },
          { title: '原部门', dataIndex: 'old_department', key: 'from' },
          { title: '新部门', dataIndex: 'new_department', key: 'to' },
          { title: '原站点', dataIndex: 'old_site', key: 'old_site' },
          { title: '新站点', dataIndex: 'new_site', key: 'new_site' },
          { title: '状态', dataIndex: 'status', key: 'status', render: (v: string) => <Tag color={statusColor(v)}>{statusLabel(v)}</Tag> },
          {
            title: '操作', key: 'action', render: (_: any, r: TransferRequest) => (
              <Button size="small" onClick={() => fetchDetail(r.request_id)}>详情</Button>
            ),
          },
        ]} rowKey="request_id" size="small" />
      </Card>

      <Modal title="新建调岗请求" open={modalOpen} onCancel={() => setModalOpen(false)} onOk={() => form.submit()} width={600}>
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item name="ad_account" label="AD账号" rules={[{ required: true }]}><Input placeholder="zhangsan@company.local" /></Form.Item>
          <Form.Item name="old_department" label="原部门" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="new_department" label="新部门" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="old_site" label="原站点" rules={[{ required: true }]}><Select options={siteOptions} /></Form.Item>
          <Form.Item name="new_site" label="新站点" rules={[{ required: true }]}><Select options={siteOptions} /></Form.Item>
          <Form.Item name="new_position" label="新职位"><Input placeholder="可选" /></Form.Item>
        </Form>
      </Modal>

      <Modal title="调岗请求详情" open={!!detailReq} onCancel={() => setDetailReq(null)} footer={null} width={700}>
        {detailReq && (
          <div>
            <Steps current={detailReq.status === 'completed' ? 2 : detailReq.status === 'in_progress' ? 1 : 0}
              items={[{ title: '提交' }, { title: '处理中' }, { title: '完成' }]} style={{ marginBottom: 24 }} />
            <Descriptions column={2} bordered size="small">
              <Descriptions.Item label="请求ID">{detailReq.request_id}</Descriptions.Item>
              <Descriptions.Item label="AD账号">{detailReq.ad_account}</Descriptions.Item>
              <Descriptions.Item label="原部门">{detailReq.old_department}</Descriptions.Item>
              <Descriptions.Item label="新部门">{detailReq.new_department}</Descriptions.Item>
              <Descriptions.Item label="原站点">{detailReq.old_site}</Descriptions.Item>
              <Descriptions.Item label="新站点">{detailReq.new_site}</Descriptions.Item>
              <Descriptions.Item label="新职位">{detailReq.new_position || '-'}</Descriptions.Item>
              <Descriptions.Item label="状态"><Tag color={statusColor(detailReq.status)}>{statusLabel(detailReq.status)}</Tag></Descriptions.Item>
            </Descriptions>
          </div>
        )}
      </Modal>
    </div>
  )
}
