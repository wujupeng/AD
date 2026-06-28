import { Card, Table, Tag, Button, Modal, Form, Input, Select, message } from 'antd'
import { useEffect, useState } from 'react'
import client from '../../api/client'

interface CardMapping {
  card_id: string
  card_type: string
  ad_account: string
  is_active: boolean
  created_at: string
}

export default function BadgeIdentityManager() {
  const [cards, setCards] = useState<CardMapping[]>([])
  const [modalOpen, setModalOpen] = useState(false)
  const [form] = Form.useForm()

  const fetchCards = async () => {
    try { const { data } = await client.get('/v1/enterprise/secure-print/card-mappings'); if (data.code === 0) setCards(data.data || []) } catch {}
  }

  useEffect(() => { fetchCards() }, [])

  const handleAdd = async (values: any) => {
    try {
      await client.post('/v1/enterprise/secure-print/card-mappings', values)
      message.success('工牌映射创建成功')
      setModalOpen(false)
      form.resetFields()
      fetchCards()
    } catch { message.error('创建失败') }
  }

  return (
    <Card title="工牌身份映射" extra={<Button type="primary" size="small" onClick={() => setModalOpen(true)}>新增映射</Button>}>
      <Table dataSource={cards} columns={[
        { title: '卡ID', dataIndex: 'card_id', key: 'card' },
        { title: '卡类型', dataIndex: 'card_type', key: 'type', render: (v: string) => <Tag>{v}</Tag> },
        { title: 'AD账号', dataIndex: 'ad_account', key: 'ad' },
        { title: '状态', dataIndex: 'is_active', key: 'active', render: (v: boolean) => <Tag color={v ? 'green' : 'red'}>{v ? '启用' : '禁用'}</Tag> },
      ]} rowKey="card_id" size="small" pagination={{ pageSize: 5 }} />

      <Modal title="新增工牌映射" open={modalOpen} onCancel={() => setModalOpen(false)} onOk={() => form.submit()}>
        <Form form={form} layout="vertical" onFinish={handleAdd}>
          <Form.Item name="card_id" label="卡ID" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="card_type" label="卡类型" rules={[{ required: true }]}>
            <Select options={[{ value: 'mifare', label: 'MIFARE' }, { value: 'prox', label: 'PROX' }, { value: 'nfc', label: 'NFC' }]} />
          </Form.Item>
          <Form.Item name="ad_account" label="AD账号" rules={[{ required: true }]}><Input /></Form.Item>
        </Form>
      </Modal>
    </Card>
  )
}