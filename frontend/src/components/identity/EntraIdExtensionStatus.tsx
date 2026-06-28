import { Card, Descriptions, Tag, Row, Col, Statistic } from 'antd'
import { useEffect, useState } from 'react'
import client from '../../api/client'

interface EntraStatus {
  connection_status: string
  sync_enabled: boolean
  last_sync_time: string | null
  synced_users: number
  synced_groups: number
  tenant_id: string | null
  domain: string | null
}

export default function EntraIdExtensionStatus() {
  const [status, setStatus] = useState<EntraStatus | null>(null)

  const fetchStatus = async () => {
    try { const { data } = await client.get('/v1/enterprise/identity/entra-extension'); if (data.code === 0) setStatus(data.data) } catch {}
  }

  useEffect(() => { fetchStatus() }, [])

  return (
    <Card title="Entra ID互联网身份扩展">
      {status ? (
        <div>
          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col span={8}><Statistic title="连接状态" value={status.connection_status || '未连接'} valueStyle={{ fontSize: 16, color: status.connection_status === 'connected' ? '#3f8600' : '#cf1322' }} /></Col>
            <Col span={8}><Statistic title="已同步用户" value={status.synced_users || 0} /></Col>
            <Col span={8}><Statistic title="已同步组" value={status.synced_groups || 0} /></Col>
          </Row>
          <Descriptions column={2} bordered size="small">
            <Descriptions.Item label="同步启用">{status.sync_enabled ? <Tag color="green">是</Tag> : <Tag color="red">否</Tag>}</Descriptions.Item>
            <Descriptions.Item label="最近同步时间">{status.last_sync_time || '-'}</Descriptions.Item>
            <Descriptions.Item label="租户ID">{status.tenant_id || '-'}</Descriptions.Item>
            <Descriptions.Item label="域名">{status.domain || '-'}</Descriptions.Item>
          </Descriptions>
        </div>
      ) : <Tag>加载中...</Tag>}
    </Card>
  )
}