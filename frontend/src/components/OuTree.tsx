import { Tree } from 'antd'
import type { DataNode } from 'antd/es/tree'
import { useEffect, useState } from 'react'
import client from '../api/client'

interface OuNode {
  dn: string
  ou_name: string
  parent_dn: string | null
  site_code: string | null
}

interface OuTreeProps {
  onSelect?: (dn: string) => void
}

function buildTree(ous: OuNode[]): DataNode[] {
  const map = new Map<string, DataNode & { children: DataNode[] }>()
  const roots: DataNode[] = []

  for (const ou of ous) {
    map.set(ou.dn, {
      key: ou.dn,
      title: ou.ou_name,
      children: [],
    })
  }

  for (const ou of ous) {
    const node = map.get(ou.dn)!
    if (ou.parent_dn && map.has(ou.parent_dn)) {
      map.get(ou.parent_dn)!.children.push(node)
    } else {
      roots.push(node)
    }
  }

  return roots
}

export default function OuTree({ onSelect }: OuTreeProps) {
  const [treeData, setTreeData] = useState<DataNode[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const fetchOus = async () => {
      setLoading(true)
      try {
        const { data } = await client.get('/org/ou-tree')
        if (data.code === 0 && data.data) {
          setTreeData(buildTree(data.data))
        }
      } finally {
        setLoading(false)
      }
    }
    fetchOus()
  }, [])

  if (loading) return <div>加载中...</div>

  return (
    <Tree
      treeData={treeData}

      defaultExpandAll
      onSelect={(keys) => {
        if (keys.length > 0 && onSelect) {
          onSelect(keys[0] as string)
        }
      }}
    />
  )
}