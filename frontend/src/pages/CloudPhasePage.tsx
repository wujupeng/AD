import { Card, Steps, Tag, Button, Modal, message } from 'antd'
import { CloudOutlined } from '@ant-design/icons'
import { useEffect, useState } from 'react'
import client from '../api/client'

interface PhaseInfo { current_phase: string; entra_id_sync_status: string | null; intune_compliance_status: string | null }

export default function CloudPhasePage() {
  const [phase, setPhase] = useState<PhaseInfo | null>(null)

  const fetchPhase = async () => {
    try {
      const { data } = await client.get('/v1/enterprise/hybrid/phase')
      if (data.code === 0) setPhase(data.data)
    } catch {}
  }

  useEffect(() => { fetchPhase() }, [])

  const handlePhaseChange = (newPhase: string) => {
    Modal.confirm({
      title: `确认切换到 ${newPhase}?`,
      content: '此操作将影响系统功能可用性',
      onOk: async () => {
        try {
          await client.put('/v1/enterprise/hybrid/phase', { new_phase: newPhase })
          message.success(`已切换到 ${newPhase}`)
          fetchPhase()
        } catch { message.error('切换失败') }
      },
    })
  }

  const phaseDesc = [
    { title: 'Phase 1 - 本地AD', desc: 'Windows Server AD + DFS + 文件服务器 + 打印服务器', features: ['AD域控', 'DFS文件', '打印服务', '本地Exchange'] },
    { title: 'Phase 2 - 混合身份', desc: 'Entra ID Connect + Exchange Online + SharePoint', features: ['混合身份', 'Exchange Online', 'OneDrive', 'Teams'] },
    { title: 'Phase 3 - 全面云化', desc: 'Intune + Zero Trust + 条件访问', features: ['Intune管理', 'Autopilot', 'Zero Trust', '条件访问'] },
  ]

  const currentIdx = phase?.current_phase === 'Phase3' ? 2 : phase?.current_phase === 'Phase2' ? 1 : 0

  return (
    <Card title="云化路线管理">
      <Steps current={currentIdx} items={phaseDesc.map(p => ({ title: p.title, description: p.desc }))} />
      <div style={{ marginTop: 24 }}>
        {phaseDesc.map((p, i) => (
          <Card key={i} style={{ marginTop: 16 }} size="small" title={p.title} extra={i === currentIdx ? <Tag color="blue">当前阶段</Tag> : i > currentIdx ? <Tag>未启用</Tag> : <Tag color="green">已完成</Tag>}>
            <div>功能: {p.features.map(f => <Tag key={f}>{f}</Tag>)}</div>
          </Card>
        ))}
      </div>
      <div style={{ marginTop: 16, textAlign: 'center' }}>
        {currentIdx < 2 && <Button type="primary" icon={<CloudOutlined />} onClick={() => handlePhaseChange(currentIdx === 0 ? 'Phase2' : 'Phase3')}>推进到下一阶段</Button>}
      </div>
    </Card>
  )
}