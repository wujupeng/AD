import { Table, Input, Select, Space, Tag } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { useEffect, useState } from 'react'
import client from '../api/client'

export interface UserRecord {
  sid: string
  username: string
  display_name: string
  email: string
  department: string
  is_enabled: boolean
  site_code: string
}

export default function UserListPage() {
  const [users, setUsers] = useState<UserRecord[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(false)
  const [search, setSearch] = useState('')
  const [siteFilter, setSiteFilter] = useState<string | undefined>()
  const [siteOptions, setSiteOptions] = useState<{ label: string; value: string }[]>([])

  const fetchSites = async () => {
    try {
      const { data } = await client.get('/v1/enterprise/settings/sites')
      if (data.code === 0 && data.data) {
        setSiteOptions(data.data.map((s: any) => ({ label: s.site_display_name || s.site_name || s.site_code, value: s.site_code })))
      }
    } catch {}
  }

  const fetchUsers = async () => {
    setLoading(true)
    try {
      const params: Record<string, string | number> = { page, page_size: 50 }
      if (siteFilter) params.site_code = siteFilter
      if (search) params.search = search
      const { data } = await client.get('/org/users', { params })
      if (data.code === 0 && data.data) {
        setUsers(data.data.items || [])
        setTotal(data.data.total || 0)
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSites()
  }, [])

  useEffect(() => {
    fetchUsers()
  }, [page, siteFilter])

  const columns: ColumnsType<UserRecord> = [
    { title: '用户名', dataIndex: 'username', key: 'username' },
    { title: '显示名', dataIndex: 'display_name', key: 'display_name' },
    { title: '邮箱', dataIndex: 'email', key: 'email' },
    { title: '部门', dataIndex: 'department', key: 'department' },
    { title: '站点', dataIndex: 'site_code', key: 'site_code' },
    {
      title: '状态',
      dataIndex: 'is_enabled',
      key: 'is_enabled',
      render: (enabled: boolean) => (
        <Tag color={enabled ? 'green' : 'red'}>{enabled ? '启用' : '禁用'}</Tag>
      ),
    },
  ]

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Input.Search
          placeholder="搜索用户"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          onSearch={fetchUsers}
          style={{ width: 300 }}
        />
        <Select
          placeholder="按站点筛选"
          allowClear
          style={{ width: 200 }}
          onChange={setSiteFilter}
          options={siteOptions}
        />
      </Space>
      <Table
        columns={columns}
        dataSource={users}
        rowKey="sid"
        loading={loading}
        pagination={{ current: page, total, pageSize: 50, onChange: setPage }}
      />
    </div>
  )
}
