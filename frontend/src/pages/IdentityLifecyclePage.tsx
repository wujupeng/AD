import { Card, Table, Tag, Input, Descriptions, Row, Col, Statistic } from 'antd'
import { useEffect, useState } from 'react'
import client from '../api/client'

interface LifecycleEvent {
  event_id: string
  ad_account: string
  event_type: string
  trigger_source: string
  event_time: string
  old_value: string | null
  new_value: string | null
  affected_systems: string[] | null
  details: Record<string, unknown> | null
}

export default function IdentityLifecyclePage() {
  const [events, setEvents] = useState<LifecycleEvent[]>([])
  const [searchAccount, setSearchAccount] = useState('')
  const [report, setReport] = useState<Record<string, unknown> | null>(null)

  const fetchEvents = async () => {
    try { const { data } = await client.get('/v1/enterprise/identity/lifecycle-events?limit=100'); if (data.code === 0) setEvents(data.data || []) } catch {}
  }

  const fetchReport = async () => {
    if (!searchAccount) return
    try {
      const { data } = await client.get(`/v1/enterprise/identity/lifecycle/${searchAccount}`)
      if (data.code === 0) setReport(data.data)
    } catch {}
  }

  useEffect(() => { fetchEvents() }, [])
  useEffect(() => { if (searchAccount) fetchReport() }, [searchAccount])

  const eventTypeColor = (t: string) => {
    const m: Record<string, string> = { onboarding: 'green', offboarding: 'red', transfer: 'blue', group_change: 'orange', ou_change: 'purple', password_reset: 'volcano', account_lock: 'magenta', onboarding_started: 'green', offboarding_started: 'red', transfer_started: 'blue' }
    return m[t] || 'default'
  }

  const eventTypeLabel = (t: string) => {
    const m: Record<string, string> = { onboarding: '入职', offboarding: '离职', transfer: '调岗', group_change: '组变更', ou_change: 'OU变更', password_reset: '密码重置', account_lock: '账号锁定', onboarding_started: '入职(开始)', offboarding_started: '离职(开始)', transfer_started: '调岗(开始)', onboarding_completed: '入职(完成)', offboarding_completed: '离职(完成)', transfer_completed: '调岗(完成)' }
    return m[t] || t
  }

  const onboardingCount = events.filter(e => e.event_type.startsWith('onboarding')).length
  const offboardingCount = events.filter(e => e.event_type.startsWith('offboarding')).length
  const transferCount = events.filter(e => e.event_type.startsWith('transfer')).length

  return (
    <div>
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col span={8}>
          <Card><Statistic title="入职事件" value={onboardingCount} valueStyle={{ color: '#3f8600' }} /></Card>
        </Col>
        <Col span={8}>
          <Card><Statistic title="离职事件" value={offboardingCount} valueStyle={{ color: '#cf1322' }} /></Card>
        </Col>
        <Col span={8}>
          <Card><Statistic title="调岗事件" value={transferCount} valueStyle={{ color: '#1677ff' }} /></Card>
        </Col>
      </Row>

      <Card title="身份生命周期查询" style={{ marginBottom: 16 }}>
        <Input.Search
          placeholder="输入AD账号查询生命周期报告"
          enterButton="查询"
          value={searchAccount}
          onChange={e => setSearchAccount(e.target.value)}
          onSearch={fetchReport}
          style={{ marginBottom: 16 }}
        />
        {report && (
          <Descriptions column={2} bordered size="small">
            <Descriptions.Item label="AD账号">{(report as any).ad_account}</Descriptions.Item>
            <Descriptions.Item label="事件总数">{(report as any).events?.length || 0}</Descriptions.Item>
          </Descriptions>
        )}
        {report && (report as any).events?.length > 0 && (
          <Table dataSource={(report as any).events} columns={[
            { title: '事件类型', dataIndex: 'event_type', key: 'type', render: (v: string) => <Tag color={eventTypeColor(v)}>{eventTypeLabel(v)}</Tag> },
            { title: '触发源', dataIndex: 'trigger_source', key: 'source' },
            { title: '时间', dataIndex: 'event_time', key: 'time', width: 180 },
            { title: '旧值', dataIndex: 'old_value', key: 'old' },
            { title: '新值', dataIndex: 'new_value', key: 'new' },
          ]} rowKey="event_time" size="small" pagination={false} style={{ marginTop: 16 }} />
        )}
      </Card>

      <Card title="最近生命周期事件">
        <Table dataSource={events} columns={[
          { title: '事件类型', dataIndex: 'event_type', key: 'type', render: (v: string) => <Tag color={eventTypeColor(v)}>{eventTypeLabel(v)}</Tag> },
          { title: 'AD账号', dataIndex: 'ad_account', key: 'account' },
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
    </div>
  )
}