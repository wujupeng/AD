import { Card, Tag, Progress } from 'antd'
import { useEffect, useState } from 'react'
import client from '../api/client'

interface TierInfo { tier_level: number; tier_name: string; server_list: string[]; admin_groups: string[]; login_restriction: string }
interface BaselineStat { total: number; compliant: number; non_compliant: number; compliance_rate: number }

export default function TierSecurityPage() {
  const [tiers, setTiers] = useState<TierInfo[]>([])
  const [stats, setStats] = useState<BaselineStat | null>(null)

  const fetchData = async () => {
    try {
      const { data } = await client.get('/v1/enterprise/tier/overview')
      if (data.code === 0) setTiers(data.data)
    } catch {}
  }

  const fetchBaseline = async () => {
    try {
      const { data } = await client.get('/v1/enterprise/tier/security-baseline')
      if (data.code === 0) setStats(data.data.statistics)
    } catch {}
  }

  useEffect(() => { fetchData(); fetchBaseline() }, [])

  const tierColors = ['red', 'orange', 'green']

  return (
    <div>
      <Card title="Tier 安全模型">
        {tiers.map((t, i) => (
          <Card.Grid key={t.tier_level} style={{ width: '33%', padding: 16 }}>
            <Tag color={tierColors[i]} style={{ fontSize: 16, marginBottom: 8 }}>Tier {t.tier_level}</Tag>
            <div style={{ fontWeight: 'bold', marginBottom: 8 }}>{t.tier_name}</div>
            <div style={{ fontSize: 12, color: '#666' }}>服务器: {t.server_list?.join(', ') || '终端'}</div>
            <div style={{ fontSize: 12, color: '#666', marginTop: 4 }}>管理组: {t.admin_groups?.join(', ')}</div>
          </Card.Grid>
        ))}
      </Card>
      <Card title="安全基线达标率" style={{ marginTop: 16 }}>
        {stats && <Progress type="circle" percent={stats.compliance_rate} format={() => `${stats.compliance_rate}%`} />}
        {stats && <div style={{ marginTop: 16 }}>总终端: {stats.total} | 合规: {stats.compliant} | 不合规: {stats.non_compliant}</div>}
      </Card>
    </div>
  )
}