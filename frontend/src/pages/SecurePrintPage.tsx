import { Card, Table, Tag, Button, Modal, Form, Input, Select, message } from 'antd'
import { IdcardOutlined } from '@ant-design/icons'
import { useEffect, useState } from 'react'
import client from '../api/client'

interface PrintJob { job_id: string; owner_account: string; document_name: string | null; pages: number; job_status: string; submitted_at: string; expires_at: string }
interface MfpPrinter { printer_name: string; site: string; ip_address: string; printer_brand: string; is_active: boolean }
interface CardMapping { card_id: string; card_type: string; ad_account: string; is_active: boolean }

export default function SecurePrintPage() {
  const [jobs, setJobs] = useState<PrintJob[]>([])
  const [printers, setPrinters] = useState<MfpPrinter[]>([])
  const [cards, setCards] = useState<CardMapping[]>([])
  const [cardModalOpen, setCardModalOpen] = useState(false)
  const [form] = Form.useForm()

  const fetchJobs = async () => {
    try { const { data } = await client.get('/v1/enterprise/secure-print/jobs'); if (data.code === 0) setJobs(data.data) } catch {}
  }
  const fetchPrinters = async () => {
    try { const { data } = await client.get('/v1/enterprise/secure-print/mfp-printers'); if (data.code === 0) setPrinters(data.data) } catch {}
  }
  const fetchCards = async () => {
    try { const { data } = await client.get('/v1/enterprise/secure-print/card-mappings'); if (data.code === 0) setCards(data.data) } catch {}
  }

  useEffect(() => { fetchJobs(); fetchPrinters(); fetchCards() }, [])

  const handleAddCard = async (values: any) => {
    try {
      await client.post('/v1/enterprise/secure-print/card-mappings', values)
      message.success('IC卡映射创建成功')
      setCardModalOpen(false)
      fetchCards()
    } catch { message.error('创建失败') }
  }

  const statusColor = (s: string) => s === 'queued' ? 'blue' : s === 'released' ? 'green' : s === 'expired' ? 'default' : 'red'

  return (
    <div>
      <Card title="Secure Print 任务队列">
        <Table dataSource={jobs} columns={[
          { title: '任务ID', dataIndex: 'job_id', key: 'id', render: (v: string) => v.substring(0, 8) + '...' },
          { title: '所有者', dataIndex: 'owner_account', key: 'owner' },
          { title: '文档', dataIndex: 'document_name', key: 'doc' },
          { title: '页数', dataIndex: 'pages', key: 'pages' },
          { title: '状态', dataIndex: 'job_status', key: 'status', render: (v: string) => <Tag color={statusColor(v)}>{v}</Tag> },
          { title: '提交时间', dataIndex: 'submitted_at', key: 'time' },
        ]} rowKey="job_id" size="small" />
      </Card>
      <Card title="MFP 打印机" style={{ marginTop: 16 }}>
        <Table dataSource={printers} columns={[
          { title: '打印机', dataIndex: 'printer_name', key: 'name' },
          { title: '站点', dataIndex: 'site', key: 'site' },
          { title: 'IP', dataIndex: 'ip_address', key: 'ip' },
          { title: '品牌', dataIndex: 'printer_brand', key: 'brand' },
          { title: '状态', dataIndex: 'is_active', key: 'active', render: (v: boolean) => v ? <Tag color="green">在线</Tag> : <Tag color="red">离线</Tag> },
        ]} rowKey="printer_name" size="small" />
      </Card>
      <Card title="IC卡/工牌映射" style={{ marginTop: 16 }} extra={<Button icon={<IdcardOutlined />} onClick={() => setCardModalOpen(true)}>添加映射</Button>}>
        <Table dataSource={cards} columns={[
          { title: '卡号', dataIndex: 'card_id', key: 'card' },
          { title: '类型', dataIndex: 'card_type', key: 'type' },
          { title: 'AD账号', dataIndex: 'ad_account', key: 'account' },
          { title: '状态', dataIndex: 'is_active', key: 'active', render: (v: boolean) => v ? <Tag color="green">有效</Tag> : <Tag color="red">停用</Tag> },
        ]} rowKey="card_id" size="small" />
      </Card>
      <Modal title="添加IC卡映射" open={cardModalOpen} onCancel={() => setCardModalOpen(false)} onOk={() => form.submit()}>
        <Form form={form} onFinish={handleAddCard} layout="vertical">
          <Form.Item name="card_id" label="卡号" rules={[{ required: true }]}><Input placeholder="IC卡/NFC卡号" /></Form.Item>
          <Form.Item name="card_type" label="卡类型" initialValue="mifare"><Select options={[{value:'mifare',label:'MIFARE'},{value:'hid',label:'HID'},{value:'nfc',label:'NFC'},{value:'pin',label:'PIN'}]} /></Form.Item>
          <Form.Item name="ad_account" label="AD账号" rules={[{ required: true }]}><Input placeholder="COMPANY\username" /></Form.Item>
        </Form>
      </Modal>
    </div>
  )
}