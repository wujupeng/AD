import { Card, Table, Button, Select, Breadcrumb, Space, Tag, message } from 'antd'
import { FolderOutlined, FileOutlined, HomeOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { useEffect, useState } from 'react'
import client from '../api/client'

interface FileItem {
  name: string
  path: string
  type: 'file' | 'directory'
  size: number
  modified: string
}

interface ShareItem {
  name: string
  type: string
  comment: string
}

const SITE_OPTIONS = [
  { value: 'cii_factory', label: 'CII工厂 (dcser1/dc4)' },
  { value: 'cii_factory_dc4', label: 'CII工厂-DC4 C$ (192.168.1.11)' },
]

const SITE_ROOT_PATHS: Record<string, string> = {
  cii_factory: '\\\\dcser1\\share',
  cii_factory_dc4: '\\\\dc4\\C$',
}

function formatSize(bytes: number): string {
  if (bytes === 0) return '-'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`
}

export default function DfsBrowserPage() {
  const [files, setFiles] = useState<FileItem[]>([])
  const [shares, setShares] = useState<ShareItem[]>([])
  const [currentPath, setCurrentPath] = useState('')
  const [pathHistory, setPathHistory] = useState<string[]>([])
  const [siteCode, setSiteCode] = useState<string>('cii_factory')
  const [loading, setLoading] = useState(false)
  const [viewMode, setViewMode] = useState<'shares' | 'files'>('shares')

  const fetchShares = async (site: string) => {
    setLoading(true)
    try {
      const { data } = await client.get('/dfs/shares', { params: { site_code: site } })
      if (data.code === 0 && Array.isArray(data.data)) {
        setShares(data.data)
        setViewMode('shares')
        setCurrentPath('')
        setPathHistory([])
      }
    } catch {
      message.error('获取共享列表失败')
    } finally {
      setLoading(false)
    }
  }

  const fetchFiles = async (path: string, site: string) => {
    setLoading(true)
    try {
      const { data } = await client.get('/dfs/files', { params: { path, site_code: site } })
      if (data.code === 0 && data.data) {
        setFiles(data.data.items || [])
        setCurrentPath(path)
        setViewMode('files')
      }
    } catch {
      message.error('获取文件列表失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchShares(siteCode)
  }, [siteCode])

  const navigateToShare = (shareName: string) => {
    const rootPath = SITE_ROOT_PATHS[siteCode] || `\\\\${shareName}`
    const path = rootPath.includes(shareName) ? rootPath : `${rootPath}\\${shareName}`
    setPathHistory([])
    fetchFiles(path, siteCode)
  }

  const navigateToFolder = (folderPath: string) => {
    setPathHistory(prev => [...prev, currentPath])
    fetchFiles(folderPath, siteCode)
  }

  const navigateBack = () => {
    if (pathHistory.length > 0) {
      const prevPath = pathHistory[pathHistory.length - 1]
      if (prevPath) {
        setPathHistory(prev => prev.slice(0, -1))
        fetchFiles(prevPath, siteCode)
      }
    } else {
      fetchShares(siteCode)
    }
  }

  const navigateHome = () => {
    fetchShares(siteCode)
  }

  const pathParts = currentPath.replace(/\\/g, '/').split('/').filter(Boolean)

  const fileColumns: ColumnsType<FileItem> = [
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      render: (name: string, record: FileItem) => (
        <Space>
          {record.type === 'directory' ? <FolderOutlined style={{ color: '#faad14' }} /> : <FileOutlined style={{ color: '#1890ff' }} />}
          <span style={{ cursor: record.type === 'directory' ? 'pointer' : 'default' }}>{name}</span>
        </Space>
      ),
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 100,
      render: (type: string) => (
        <Tag color={type === 'directory' ? 'blue' : 'default'}>{type === 'directory' ? '文件夹' : '文件'}</Tag>
      ),
    },
    {
      title: '大小',
      dataIndex: 'size',
      key: 'size',
      width: 120,
      render: (size: number, record: FileItem) => record.type === 'directory' ? '-' : formatSize(size),
    },
    {
      title: '修改时间',
      dataIndex: 'modified',
      key: 'modified',
      width: 200,
    },
  ]

  const shareColumns: ColumnsType<ShareItem> = [
    {
      title: '共享名',
      dataIndex: 'name',
      key: 'name',
      render: (name: string) => <Space><FolderOutlined style={{ color: '#faad14' }} /><a onClick={() => navigateToShare(name)}>{name}</a></Space>,
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 100,
      render: (type: string) => <Tag>{type}</Tag>,
    },
    {
      title: '备注',
      dataIndex: 'comment',
      key: 'comment',
    },
  ]

  return (
    <Card
      title={
        <Space>
          <HomeOutlined />
          <span>共享文件浏览</span>
          <Select
            value={siteCode}
            onChange={(v) => setSiteCode(v)}
            style={{ width: 250, marginLeft: 16 }}
            options={SITE_OPTIONS}
          />
        </Space>
      }
      extra={
        <Space>
          <Button onClick={navigateHome} icon={<HomeOutlined />}>根目录</Button>
          <Button onClick={navigateBack} disabled={viewMode === 'shares' && pathHistory.length === 0}>上一级</Button>
        </Space>
      }
    >
      {viewMode === 'files' && currentPath && (
        <Breadcrumb style={{ marginBottom: 16 }}>
          <Breadcrumb.Item>
            <a onClick={navigateHome}>共享</a>
          </Breadcrumb.Item>
          {pathParts.map((part, idx) => (
            <Breadcrumb.Item key={idx}>
              {idx === pathParts.length - 1 ? part : part}
            </Breadcrumb.Item>
          ))}
        </Breadcrumb>
      )}

      {viewMode === 'shares' ? (
        <Table
          columns={shareColumns}
          dataSource={shares}
          rowKey="name"
          loading={loading}
          size="small"
          pagination={false}
        />
      ) : (
        <Table
          columns={fileColumns}
          dataSource={files}
          rowKey="path"
          loading={loading}
          size="small"
          pagination={{ pageSize: 50 }}
          onRow={(record) => ({
            onDoubleClick: () => {
              if (record.type === 'directory') {
                navigateToFolder(record.path)
              }
            },
            style: { cursor: record.type === 'directory' ? 'pointer' : 'default' },
          })}
        />
      )}
    </Card>
  )
}
