import { Card, Table, Tag, Input } from 'antd'
import { useEffect, useState } from 'react'
import client from '../../api/client'

interface LifecycleAuditEvent {
  event_id: string
  ad_account: string
  event_type: string
  trigger_source: string
  event_time: string
  old_value: string | null
  new_value: string | null
  affected_systems: string[] | null
}

export default function LifecycleAuditPanel() {
  const [events, setEvents] = useState<LifecycleAuditEvent[]>([])
  const [searchAccount, setSearchAccount] = useState('')

  const fetchEvents = async () => {
    try { const { data } = await client.get('/v1/enterprise/identity/audit/lifecycle?limit=50'); if (data.code === 0) setEvents(data.data || []) } catch {}
  }

  useEffect(() => { fetchEvents() }, [])

  const eventTypeColor = (t: string) => {
    const m: Record<string, string> = { onboarding: 'green', offboarding: 'red', transfer: 'blue', group_change: 'orange', ou_change: 'purple', password_reset: 'volcano', account_lock: 'magenta' }
    return m[t] || 'default'
  }

  return (
    <Card title="身份生命周期审计">
      <Input.Search
        placeholder="按AD账号筛选"
        allowClear
        style={{ marginBottom: 16, maxWidth: 300 }}
        onSearch={v => setSearchAccount(v)}
        onChange={e => { if (!e.target.value) setSearchAccount('') }}
      />
      <Table dataSource={searchAccount ? events.filter(e => e.ad_account?.includes(searchAccount)) : events} columns={[
        { title: 'AD账号', dataIndex: 'ad_account', key: 'ad' },
        { title: '事件类型', dataIndex: 'event_type', key: 'type', render: (v: string) => <Tag color={eventTypeColor(v)}>{v}</Tag> },
        { title: '触发源', dataIndex: 'trigger_source', key: 'source' },
        { title: '时间', dataIndex: 'event_time', key: 'time', width: 180 },
        { title: '旧值', dataIndex: 'old_value', key: 'old', ellipsis: true },
        { title: '新值', dataIndex: 'new_value', key: 'new', ellipsis: true },
        {
          title: '受影响系统', dataIndex: 'affected_systems', key: 'sys', render: (v: string[] | null) =>
            v ? v.map(s => <Tag key={s} color="blue">{s}</Tag>) : '-',
        },
      ]} rowKey="event_id" size="small" />
    </Card>
  )
}