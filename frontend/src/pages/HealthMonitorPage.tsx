import { Card, Row, Col, Statistic, Tag, Table, Switch, Button, Space } from 'antd'
import { useEffect, useState, useRef } from 'react'
import { ReloadOutlined } from '@ant-design/icons'
import client from '../api/client'

interface ComponentStatus {
  status: string
  [key: string]: any
}

interface HealthDetail {
  status: string
  timestamp: string
  components: {
    ad_domain_controller: ComponentStatus
    postgresql: ComponentStatus
    redis: ComponentStatus
    nginx: ComponentStatus
    backend_service: ComponentStatus
  }
}

const statusColor = (s: string) => {
  const m: Record<string, string> = { healthy: 'green', degraded: 'orange', unhealthy: 'red', error: 'red', offline: 'default', unavailable: 'default' }
  return m[s] || 'default'
}
const statusIcon = (s: string) => {
  const m: Record<string, string> = { healthy: '🟢', degraded: '🟡', unhealthy: '🔴', error: '🔴', offline: '⚪', unavailable: '⚪' }
  return m[s] || '⚪'
}
const statusLabel = (s: string) => {
  const m: Record<string, string> = { healthy: '正常', degraded: '降级', unhealthy: '异常', error: '错误', offline: '离线', unavailable: '不可用' }
  return m[s] || s
}

export default function HealthMonitorPage() {
  const [health, setHealth] = useState<HealthDetail | null>(null)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [loading, setLoading] = useState(false)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const fetchHealth = async () => {
    setLoading(true)
    try {
      const { data } = await client.get('/health/detail')
      if (data.code === 0 && data.data) setHealth(data.data)
    } catch {}
    setLoading(false)
  }

  useEffect(() => {
    fetchHealth()
  }, [])

  useEffect(() => {
    if (autoRefresh) {
      intervalRef.current = setInterval(fetchHealth, 30000)
    }
    return () => { if (intervalRef.current) clearInterval(intervalRef.current) }
  }, [autoRefresh])

  const ad = health?.components?.ad_domain_controller
  const pg = health?.components?.postgresql
  const rd = health?.components?.redis
  const nx = health?.components?.nginx
  const bs = health?.components?.backend_service

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button icon={<ReloadOutlined />} onClick={fetchHealth} loading={loading}>刷新</Button>
        <span>自动刷新</span>
        <Switch checked={autoRefresh} onChange={setAutoRefresh} />
        <Tag color={statusColor(health?.status || '')} style={{ fontSize: 14, padding: '2px 12px' }}>
          整体状态: {statusLabel(health?.status || '')}
        </Tag>
      </Space>

      <Row gutter={[16, 16]}>
        <Col span={8}>
          <Card title={<span>{statusIcon(ad?.status || '')} AD域控</span>} size="small">
            <Statistic title="状态" value={statusLabel(ad?.status || '')} valueStyle={{ fontSize: 14, color: ad?.status === 'healthy' ? '#3f8600' : '#cf1322' }} />
            <Statistic title="DC主机" value={ad?.dc_host ?? '-'} valueStyle={{ fontSize: 12 }} />
            <Statistic title="复制状态" value={ad?.replication_status ?? '-'} valueStyle={{ fontSize: 12 }} />
            {ad?.fsmo_roles && ad.fsmo_roles.length > 0 && <div style={{ marginTop: 8 }}>FSMO: {ad.fsmo_roles.map((r: string) => <Tag key={r} color="blue" style={{ margin: 2 }}>{r}</Tag>)}</div>}
          </Card>
        </Col>
        <Col span={8}>
          <Card title={<span>{statusIcon(pg?.status || '')} PostgreSQL</span>} size="small">
            <Statistic title="活跃连接" value={pg?.active_connections || 0} suffix={`/ ${pg?.max_connections || 0}`} valueStyle={{ fontSize: 12 }} />
            <Statistic title="连接使用率" value={pg?.connection_usage_percent || 0} suffix="%" valueStyle={{ fontSize: 12, color: (pg?.connection_usage_percent || 0) > 80 ? '#cf1322' : '#3f8600' }} />
            <Statistic title="慢查询数" value={pg?.slow_queries_count || 0} valueStyle={{ fontSize: 12 }} />
          </Card>
        </Col>
        <Col span={8}>
          <Card title={<span>{statusIcon(rd?.status || '')} Redis</span>} size="small">
            <Statistic title="内存使用" value={rd?.used_memory_mb || 0} suffix={`MB / ${rd?.max_memory_mb || 0}MB`} valueStyle={{ fontSize: 12 }} />
            <Statistic title="命中率" value={rd?.hit_rate_percent || 0} suffix="%" valueStyle={{ fontSize: 12, color: (rd?.hit_rate_percent || 0) < 80 ? '#cf1322' : '#3f8600' }} />
            <Statistic title="键总数" value={rd?.total_keys || 0} valueStyle={{ fontSize: 12 }} />
          </Card>
        </Col>
        <Col span={8}>
          <Card title={<span>{statusIcon(nx?.status || '')} Nginx</span>} size="small">
            <Statistic title="活跃连接" value={nx?.active_connections || 0} valueStyle={{ fontSize: 12 }} />
            <Statistic title="Reading/Writing/Waiting" value={`${nx?.reading || 0} / ${nx?.writing || 0} / ${nx?.waiting || 0}`} valueStyle={{ fontSize: 12 }} />
            <Statistic title="总请求数" value={nx?.total_requests || 0} valueStyle={{ fontSize: 12 }} />
          </Card>
        </Col>
        <Col span={8}>
          <Card title={<span>{statusIcon(bs?.status || '')} 后端服务</span>} size="small">
            <Statistic title="CPU" value={bs?.cpu_usage_percent || 0} suffix="%" valueStyle={{ fontSize: 12 }} />
            <Statistic title="内存RSS" value={bs?.memory_rss_mb || 0} suffix="MB" valueStyle={{ fontSize: 12 }} />
            <Statistic title="平均延迟" value={bs?.avg_request_latency_ms || 0} suffix="ms" valueStyle={{ fontSize: 12 }} />
            <Statistic title="运行时间" value={Math.floor((bs?.uptime_seconds || 0) / 3600)} suffix="小时" valueStyle={{ fontSize: 12 }} />
          </Card>
        </Col>
      </Row>

      {pg?.slow_queries && pg.slow_queries.length > 0 && (
        <Card title="PostgreSQL 慢查询" style={{ marginTop: 16 }} size="small">
          <Table dataSource={pg.slow_queries} columns={[
            { title: 'SQL', dataIndex: 'query_text', key: 'query', ellipsis: true },
            { title: '平均耗时(ms)', dataIndex: 'duration_ms', key: 'dur', width: 120, render: (v: number) => <span style={{ color: v > 2000 ? '#cf1322' : undefined }}>{v}</span> },
            { title: '调用次数', dataIndex: 'calls', key: 'calls', width: 100 },
          ]} rowKey="query_text" size="small" pagination={false} />
        </Card>
      )}

      {pg?.table_sizes && pg.table_sizes.length > 0 && (
        <Card title="PostgreSQL 表大小 TOP10" style={{ marginTop: 16 }} size="small">
          <Table dataSource={pg.table_sizes} columns={[
            { title: '表名', dataIndex: 'table_name', key: 'name' },
            { title: '大小(MB)', dataIndex: 'size_mb', key: 'size', sorter: (a: any, b: any) => a.size_mb - b.size_mb },
            { title: '行数', dataIndex: 'row_count', key: 'rows' },
          ]} rowKey="table_name" size="small" pagination={false} />
        </Card>
      )}
    </div>
  )
}
