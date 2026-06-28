import { Card, Table, Tag } from 'antd'
import { useEffect, useState } from 'react'
import client from '../api/client'

interface SdwanLink { link_id: string; source_site: string; target_site: string; bandwidth_mbps: number | null; latency_ms: number | null; packet_loss_percent: number | null; link_status: string }

export default function SdwanStatusPage() {
  const [links, setLinks] = useState<SdwanLink[]>([])
  const [impact, setImpact] = useState<any>(null)

  const fetchData = async () => {
    try {
      const { data } = await client.get('/v1/enterprise/sdwan/links')
      if (data.code === 0) setLinks(data.data)
    } catch {}
  }

  const fetchImpact = async () => {
    try {
      const { data } = await client.get('/v1/enterprise/sdwan/impact-analysis')
      if (data.code === 0) setImpact(data.data)
    } catch {}
  }

  useEffect(() => { fetchData(); fetchImpact() }, [])

  const columns = [
    { title: '源站点', dataIndex: 'source_site', key: 'src' },
    { title: '目标站点', dataIndex: 'target_site', key: 'tgt' },
    { title: '带宽(Mbps)', dataIndex: 'bandwidth_mbps', key: 'bw' },
    { title: '延迟(ms)', dataIndex: 'latency_ms', key: 'lat', render: (v: number) => v && v > 200 ? <Tag color="red">{v}</Tag> : v },
    { title: '丢包(%)', dataIndex: 'packet_loss_percent', key: 'loss', render: (v: number) => v && v > 5 ? <Tag color="red">{v}</Tag> : v },
    { title: '状态', dataIndex: 'link_status', key: 'status', render: (v: string) => {
      const color = v === 'up' ? 'green' : v === 'degraded' ? 'orange' : 'red'
      return <Tag color={color}>{v}</Tag>
    }},
  ]

  return (
    <div>
      <Card title="SD-WAN 链路状态">
        <Table dataSource={links} columns={columns} rowKey="link_id" pagination={false} size="small" />
      </Card>
      {impact && impact.impacted_services?.length > 0 && (
        <Card title="网络影响分析" style={{ marginTop: 16 }}>
          {impact.impacted_services.map((s: any, i: number) => (
            <div key={i} style={{ marginBottom: 8 }}>
              <Tag color="red">{s.link}</Tag> → 受影响: {s.affected_services?.map((f: string) => <Tag key={f}>{f}</Tag>)}
            </div>
          ))}
        </Card>
      )}
    </div>
  )
}