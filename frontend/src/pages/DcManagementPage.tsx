import { Card, Table, Tag, Button } from 'antd'
import { ReloadOutlined } from '@ant-design/icons'
import { useState, useEffect } from 'react'
import client from '../api/client'

interface DcInfo {
  dc_hostname: string
  dc_site: string
  dc_ip_address: string
  is_gc: boolean
  health_status: string
  fsmo_roles: string[]
  os_version: string
}

export default function DcManagementPage() {
  const [dcs, setDcs] = useState<DcInfo[]>([])
  const [loading, setLoading] = useState(false)
  const [fsmoRoles, setFsmoRoles] = useState<Record<string, string>>({})

  const fetchDcs = async () => {
    setLoading(true)
    try {
      const { data } = await client.get('/v1/enterprise/dc')
      if (data.code === 0) setDcs(data.data)
    } catch {}
    setLoading(false)
  }

  const fetchFsmo = async () => {
    try {
      const { data } = await client.get('/v1/enterprise/dc/fsmo-roles')
      if (data.code === 0) setFsmoRoles(data.data)
    } catch {}
  }

  useEffect(() => { fetchDcs(); fetchFsmo() }, [])

  const columns = [
    { title: 'DC主机名', dataIndex: 'dc_hostname', key: 'hostname' },
    { title: '站点', dataIndex: 'dc_site', key: 'site' },
    { title: 'IP地址', dataIndex: 'dc_ip_address', key: 'ip' },
    { title: 'GC', dataIndex: 'is_gc', key: 'gc', render: (v: boolean) => v ? <Tag color="green">是</Tag> : <Tag>否</Tag> },
    { title: '健康状态', dataIndex: 'health_status', key: 'health', render: (v: string) => {
      const color = v === 'healthy' ? 'green' : v === 'unreachable' ? 'red' : 'orange'
      return <Tag color={color}>{v}</Tag>
    }},
    { title: 'FSMO角色', dataIndex: 'fsmo_roles', key: 'fsmo', render: (roles: string[]) => roles?.map((r: string) => <Tag key={r} color="blue">{r}</Tag>) },
    { title: 'OS版本', dataIndex: 'os_version', key: 'os' },
  ]

  return (
    <div>
      <Card title="域控制器管理" extra={<Button icon={<ReloadOutlined />} onClick={fetchDcs} loading={loading}>刷新</Button>}>
        <Table dataSource={dcs} columns={columns} rowKey="dc_hostname" pagination={false} size="small" />
      </Card>
      <Card title="FSMO角色分布" style={{ marginTop: 16 }}>
        {Object.entries(fsmoRoles).map(([role, dc]) => (
          <div key={role} style={{ marginBottom: 8 }}><Tag color="blue">{role}</Tag> → <strong>{dc}</strong></div>
        ))}
      </Card>
    </div>
  )
}