import { Card, Table, Tag, Button } from 'antd'
import { ReloadOutlined } from '@ant-design/icons'
import { useEffect, useState } from 'react'
import client from '../api/client'

interface AlertInfo { alert_id: string; source_system: string; severity: string; category: string; title: string; trigger_time: string; acknowledged: boolean; resolved: boolean }

export default function AlertPanelPage() {
  const [alerts, setAlerts] = useState<AlertInfo[]>([])

  const fetchAlerts = async () => {
    try {
      const { data } = await client.get('/v1/enterprise/monitoring/alerts')
      if (data.code === 0) setAlerts(data.data)
    } catch {}
  }

  useEffect(() => { fetchAlerts() }, [])

  const handleAck = async (alertId: string) => {
    try {
      await client.put(`/v1/enterprise/monitoring/alerts/${alertId}/acknowledge`)
      fetchAlerts()
    } catch {}
  }

  const sevColor = (s: string) => s === 'critical' ? 'red' : s === 'warning' ? 'orange' : 'blue'

  const columns = [
    { title: '严重级别', dataIndex: 'severity', key: 'sev', render: (v: string) => <Tag color={sevColor(v)}>{v}</Tag> },
    { title: '来源', dataIndex: 'source_system', key: 'src' },
    { title: '类别', dataIndex: 'category', key: 'cat' },
    { title: '标题', dataIndex: 'title', key: 'title' },
    { title: '触发时间', dataIndex: 'trigger_time', key: 'time' },
    { title: '状态', key: 'status', render: (_: any, r: AlertInfo) => r.resolved ? <Tag color="green">已解决</Tag> : r.acknowledged ? <Tag color="orange">已确认</Tag> : <Tag color="red">待处理</Tag> },
    { title: '操作', key: 'action', render: (_: any, r: AlertInfo) => !r.acknowledged && <Button size="small" onClick={() => handleAck(r.alert_id)}>确认</Button> },
  ]

  return (
    <Card title="统一告警面板" extra={<Button icon={<ReloadOutlined />} onClick={fetchAlerts}>刷新</Button>}>
      <Table dataSource={alerts} columns={columns} rowKey="alert_id" size="small" />
    </Card>
  )
}