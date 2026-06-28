import { Table, Select, Space, Tag, Button } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { useEffect, useState } from 'react'
import client from '../api/client'

interface AuditLogRecord {
  id: number
  event_type: string
  user_sid: string | null
  username: string | null
  site_code: string | null
  resource: string | null
  action: string | null
  result: string
  occurred_at: string | null
}

export default function AuditLogPage() {
  const [logs, setLogs] = useState<AuditLogRecord[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(false)
  const [eventType, setEventType] = useState<string | undefined>()

  const fetchLogs = async () => {
    setLoading(true)
    try {
      const params: Record<string, string | number> = { page, page_size: 50 }
      if (eventType) params.event_type = eventType
      const { data } = await client.get('/audit/logs', { params })
      if (data.code === 0 && data.data) {
        setLogs(data.data.items || [])
        setTotal(data.data.total || 0)
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchLogs()
  }, [page, eventType])

  const columns: ColumnsType<AuditLogRecord> = [
    { title: '事件类型', dataIndex: 'event_type', key: 'event_type', width: 200 },
    { title: '用户', dataIndex: 'username', key: 'username', width: 120 },
    { title: '站点', dataIndex: 'site_code', key: 'site_code', width: 100 },
    { title: '资源', dataIndex: 'resource', key: 'resource', width: 200, ellipsis: true },
    { title: '操作', dataIndex: 'action', key: 'action', width: 100 },
    {
      title: '结果',
      dataIndex: 'result',
      key: 'result',
      width: 80,
      render: (result: string) => (
        <Tag color={result === 'success' ? 'green' : 'red'}>{result}</Tag>
      ),
    },
    { title: '时间', dataIndex: 'occurred_at', key: 'occurred_at', width: 180 },
  ]

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Select
          placeholder="事件类型"
          allowClear
          style={{ width: 200 }}
          onChange={setEventType}
          options={[
            { label: '登录成功', value: 'AUTH_LOGIN_SUCCESS' },
            { label: '登录失败', value: 'AUTH_LOGIN_FAILED' },
            { label: '账户锁定', value: 'AUTH_ACCOUNT_LOCKED' },
            { label: 'Kerberos认证', value: 'AUTH_KERBEROS_SUCCESS' },
            { label: 'SAML SSO', value: 'SAML_SSO_SUCCESS' },
            { label: '组织同步', value: 'ORG_SYNC_COMPLETED' },
            { label: '注销', value: 'AUTH_LOGOUT' },
          ]}
        />
        <Button type="primary" onClick={fetchLogs}>刷新</Button>
      </Space>
      <Table
        columns={columns}
        dataSource={logs}
        rowKey="id"
        loading={loading}
        pagination={{ current: page, total, pageSize: 50, onChange: setPage }}
        scroll={{ x: 1000 }}
      />
    </div>
  )
}