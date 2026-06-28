import { Card, Table, Tag, Statistic, Row, Col } from 'antd'
import { useEffect, useState } from 'react'
import client from '../../api/client'

interface PrintCostRecord {
  audit_id: string
  ad_account: string
  printer_name: string
  pages: number
  cost_center: string | null
  print_time: string
}

export default function PrintConvergenceManager() {
  const [records, setRecords] = useState<PrintCostRecord[]>([])
  const [convergence, setConvergence] = useState<Record<string, unknown> | null>(null)

  const fetchRecords = async () => {
    try { const { data } = await client.get('/v1/enterprise/identity/print-cost-audit?limit=20'); if (data.code === 0) setRecords(data.data || []) } catch {}
  }
  const fetchConvergence = async () => {
    try { const { data } = await client.get('/v1/enterprise/identity/print-convergence'); if (data.code === 0) setConvergence(data.data) } catch {}
  }

  useEffect(() => { fetchRecords(); fetchConvergence() }, [])

  return (
    <Card title="打印融合与成本审计">
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={8}><Statistic title="融合状态" value={convergence ? '已配置' : '未配置'} valueStyle={{ fontSize: 16 }} /></Col>
        <Col span={8}><Statistic title="审计记录数" value={records.length} /></Col>
        <Col span={8}><Statistic title="总打印页数" value={records.reduce((s, r) => s + (r.pages || 0), 0)} /></Col>
      </Row>
      <Table dataSource={records} columns={[
        { title: 'AD账号', dataIndex: 'ad_account', key: 'ad' },
        { title: '打印机', dataIndex: 'printer_name', key: 'printer' },
        { title: '页数', dataIndex: 'pages', key: 'pages' },
        { title: '成本中心', dataIndex: 'cost_center', key: 'cost', render: (v: string | null) => v ? <Tag>{v}</Tag> : '-' },
        { title: '时间', dataIndex: 'print_time', key: 'time', width: 180 },
      ]} rowKey="audit_id" size="small" pagination={{ pageSize: 5 }} />
    </Card>
  )
}