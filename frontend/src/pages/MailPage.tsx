import { Card, Table, Input, Button, Space, Tag } from 'antd'
import { MailOutlined } from '@ant-design/icons'
import { useEffect, useState } from 'react'
import client from '../api/client'

interface ContactRecord {
  dn: string
  display_name: string
  email: string
  department: string
  title: string
  phone: string
  site_code: string
}

export default function MailPage() {
  const [contacts, setContacts] = useState<ContactRecord[]>([])
  const [loading, setLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  const fetchContacts = async (q?: string) => {
    setLoading(true)
    try {
      const query = q || searchQuery || '*'
      const { data } = await client.get('/contacts', { params: { q: query } })
      if (data.code === 0 && data.data) {
        setContacts(data.data.items || data.data || [])
      }
    } catch {
      setContacts([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchContacts('*')
  }, [])

  const columns = [
    { title: '姓名', dataIndex: 'display_name', key: 'display_name' },
    { title: '邮箱', dataIndex: 'email', key: 'email', render: (v: string) => v ? <a href={`mailto:${v}`}>{v}</a> : '-' },
    { title: '部门', dataIndex: 'department', key: 'department', render: (v: string) => v || '-' },
    { title: '职位', dataIndex: 'title', key: 'title', render: (v: string) => v || '-' },
    { title: '电话', dataIndex: 'phone', key: 'phone', render: (v: string) => v || '-' },
    { title: '站点', dataIndex: 'site_code', key: 'site_code', render: (v: string) => v ? <Tag>{v}</Tag> : '-' },
  ]

  return (
    <div>
      <Card title="邮件通讯录" extra={<Space><Input.Search placeholder="搜索联系人" value={searchQuery} onChange={e => setSearchQuery(e.target.value)} onSearch={v => fetchContacts(v)} style={{ width: 300 }} /><Button icon={<MailOutlined />}>发送邮件</Button></Space>}>
        <Table dataSource={contacts} columns={columns} rowKey="dn" loading={loading} pagination={{ pageSize: 20 }} size="small" />
      </Card>
    </div>
  )
}