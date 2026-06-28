import { Card, Table, Tag } from 'antd'
import { useEffect, useState } from 'react'
import client from '../api/client'

interface DfsLink {
  link_id: string
  source_site: string
  target_site: string
  backlog_count: number
  sync_latency_seconds: number | null
  bandwidth_usage_mbps: number | null
  link_status: string
}

export default function DfsReplicationPage() {
  const [links, setLinks] = useState<DfsLink[]>([])

  const fetchData = async () => {
    try {
      const { data } = await client.get('/v1/enterprise/dfs/replication-status')
      if (data.code === 0) setLinks(data.data)
    } catch {}
  }

  useEffect(() => { fetchData() }, [])

  const columns = [
    { title: '源站点', dataIndex: 'source_site', key: 'src' },
    { title: '目标站点', dataIndex: 'target_site', key: 'tgt' },
    { title: '积压量', dataIndex: 'backlog_count', key: 'backlog', render: (v: number) => v > 10000 ? <Tag color="red">{v}</Tag> : v },
    { title: '同步延迟(s)', dataIndex: 'sync_latency_seconds', key: 'latency' },
    { title: '带宽(Mbps)', dataIndex: 'bandwidth_usage_mbps', key: 'bw' },
    { title: '状态', dataIndex: 'link_status', key: 'status', render: (v: string) => {
      const color = v === 'healthy' ? 'green' : v === 'degraded' ? 'orange' : 'red'
      return <Tag color={color}>{v}</Tag>
    }},
  ]

  return (
    <Card title="DFS-R 复制状态">
      <Table dataSource={links} columns={columns} rowKey="link_id" pagination={false} size="small" />
    </Card>
  )
}