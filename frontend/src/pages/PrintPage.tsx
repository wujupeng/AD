import { Card, Table, Progress } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { useEffect, useState } from 'react'
import client from '../api/client'

interface Printer {
  name: string
  site: string
  status: string
}

export default function PrintPage() {
  const [printers, setPrinters] = useState<Printer[]>([])
  const [quota, setQuota] = useState({ pages_used: 0, pages_limit: 500, remaining: 500 })
  const [loading, setLoading] = useState(false)

  const fetchPrinters = async () => {
    setLoading(true)
    try {
      const { data } = await client.get('/printers')
      if (data.code === 0 && data.data) {
        setPrinters(data.data)
      }
    } finally {
      setLoading(false)
    }
  }

  const fetchQuota = async () => {
    try {
      const { data } = await client.get('/print-quota')
      if (data.code === 0 && data.data) {
        setQuota(data.data)
      }
    } catch {
      // ignore
    }
  }

  useEffect(() => {
    fetchPrinters()
    fetchQuota()
  }, [])


  const columns: ColumnsType<Printer> = [
    { title: '打印机', dataIndex: 'name', key: 'name' },
    { title: '站点', dataIndex: 'site', key: 'site' },
    { title: '状态', dataIndex: 'status', key: 'status' },
  ]

  return (
    <div>
      <Card title="打印配额" style={{ marginBottom: 16 }}>
        <Progress
          percent={Math.round((quota.pages_used / quota.pages_limit) * 100)}
          format={() => `${quota.pages_used} / ${quota.pages_limit} 页`}
          status={quota.pages_used > quota.pages_limit * 0.8 ? 'exception' : 'active'}
        />
      </Card>
      <Card title="打印机列表">
        <Table columns={columns} dataSource={printers} rowKey="name" loading={loading} />
      </Card>
    </div>
  )
}