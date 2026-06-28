import { Card, Table, Tag, Button, Modal, Form, Input, Select, Space, message, Steps, Descriptions } from 'antd'
import { useEffect, useState } from 'react'
import client from '../api/client'

interface OnboardingRequest {
  request_id: string
  employee_name: string
  department: string
  position: string
  site: string
  sam_account_name: string
  card_id: string | null
  card_type: string | null
  device_type: string | null
  manager_account: string | null
  status: string
  created_at: string
}

export default function HrOnboardingPage() {
  const [requests, setRequests] = useState<OnboardingRequest[]>([])
  const [modalOpen, setModalOpen] = useState(false)
  const [detailReq, setDetailReq] = useState<OnboardingRequest | null>(null)
  const [siteOptions, setSiteOptions] = useState<{ value: string; label: string }[]>([])
  const [form] = Form.useForm()

  const fetchRequests = async () => {
    try { const { data } = await client.get('/v1/enterprise/identity/onboarding?limit=50'); if (data.code === 0) setRequests(data.data || []) } catch {}
  }

  const fetchSites = async () => {
    try {
      const { data } = await client.get('/v1/enterprise/settings/sites')
      if (data.code === 0 && data.data) setSiteOptions(data.data.map((s: any) => ({ value: s.site_code, label: s.site_display_name || s.site_name || s.site_code })))
    } catch {}
  }

  useEffect(() => { fetchRequests(); fetchSites() }, [])

  const handleSubmit = async (values: any) => {
    try {
      await client.post('/v1/enterprise/identity/onboarding', values)
      message.success('入职请求已创建')
      setModalOpen(false)
      form.resetFields()
      fetchRequests()
    } catch { message.error('创建失败') }
  }

  const fetchDetail = async (requestId: string) => {
    try {
      const { data } = await client.get(`/v1/enterprise/identity/onboarding/${requestId}`)
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
      <Card title="HR入职管理" extra={<Button type="primary" onClick={() => setModalOpen(true)}>新建入职请求</Button>}>
        <Table dataSource={requests} columns={[
          { title: '请求ID', dataIndex: 'request_id', key: 'id', render: (v: string) => v?.substring(0, 8) + '...' },
          { title: '员工姓名', dataIndex: 'employee_name', key: 'name' },
          { title: 'AD账号', dataIndex: 'sam_account_name', key: 'sam' },
          { title: '部门', dataIndex: 'department', key: 'dept' },
          { title: '站点', dataIndex: 'site', key: 'site' },
          { title: '状态', dataIndex: 'status', key: 'status', render: (v: string) => <Tag color={statusColor(v)}>{statusLabel(v)}</Tag> },
          {
            title: '操作', key: 'action', render: (_: any, r: OnboardingRequest) => (
              <Space>
                <Button size="small" onClick={() => fetchDetail(r.request_id)}>详情</Button>
                {(r.status === 'pending' || r.status === 'partial_failed') && (
                  <Button size="small" type="primary" onClick={async () => { try { await client.post(`/v1/enterprise/identity/onboarding/${r.request_id}/execute`); message.success('入职执行成功'); fetchRequests() } catch { message.error('执行失败') } }}>执行入职</Button>
                )}
              </Space>
            ),
          },
        ]} rowKey="request_id" size="small" />
      </Card>

      <Modal title="新建入职请求" open={modalOpen} onCancel={() => setModalOpen(false)} onOk={() => form.submit()} width={600}>
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item name="employee_name" label="员工姓名" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="sam_account_name" label="AD账号名" rules={[{ required: true }]}><Input placeholder="zhangsan" /></Form.Item>
          <Form.Item name="department" label="部门" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="position" label="职位" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="site" label="站点" rules={[{ required: true }]}>
            <Select options={siteOptions} placeholder="选择站点" />
          </Form.Item>
          <Form.Item name="card_id" label="工牌ID"><Input placeholder="可选" /></Form.Item>
          <Form.Item name="card_type" label="工牌类型">
            <Select allowClear placeholder="可选" options={[
              { value: 'ic_card', label: 'IC卡' },
              { value: 'nfc_mifare', label: 'NFC MIFARE' },
              { value: 'nfc_hid', label: 'NFC HID' },
              { value: 'employee_badge', label: '员工工牌' },
            ]} />
          </Form.Item>
          <Form.Item name="device_type" label="设备类型">
            <Select allowClear placeholder="可选" options={[
              { value: 'enterprise_laptop', label: '企业笔记本' },
              { value: 'enterprise_desktop', label: '企业台式机' },
              { value: 'kiosk', label: 'Kiosk终端' },
            ]} />
          </Form.Item>
          <Form.Item name="manager_account" label="直属经理账号"><Input placeholder="可选" /></Form.Item>
        </Form>
      </Modal>

      <Modal title="入职请求详情" open={!!detailReq} onCancel={() => setDetailReq(null)} footer={null} width={700}>
        {detailReq && (
          <div>
            <Steps current={detailReq.status === 'completed' ? 2 : detailReq.status === 'in_progress' ? 1 : 0}
              items={[{ title: '提交' }, { title: '处理中' }, { title: '完成' }]} style={{ marginBottom: 24 }} />
            <Descriptions column={2} bordered size="small">
              <Descriptions.Item label="请求ID">{detailReq.request_id}</Descriptions.Item>
              <Descriptions.Item label="员工姓名">{detailReq.employee_name}</Descriptions.Item>
              <Descriptions.Item label="AD账号">{detailReq.sam_account_name}</Descriptions.Item>
              <Descriptions.Item label="部门">{detailReq.department}</Descriptions.Item>
              <Descriptions.Item label="职位">{detailReq.position}</Descriptions.Item>
              <Descriptions.Item label="站点">{detailReq.site}</Descriptions.Item>
              <Descriptions.Item label="工牌ID">{detailReq.card_id || '-'}</Descriptions.Item>
              <Descriptions.Item label="状态"><Tag color={statusColor(detailReq.status)}>{statusLabel(detailReq.status)}</Tag></Descriptions.Item>
            </Descriptions>
          </div>
        )}
      </Modal>
    </div>
  )
}
