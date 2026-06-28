import { Descriptions, Drawer, Tag } from 'antd'
import type { UserRecord } from '../pages/UserListPage'

interface UserDetailDrawerProps {
  user: UserRecord | null
  open: boolean
  onClose: () => void
}

export default function UserDetailDrawer({ user, open, onClose }: UserDetailDrawerProps) {
  if (!user) return null

  return (
    <Drawer title={user.display_name || user.username} open={open} onClose={onClose} width={500}>
      <Descriptions column={1} bordered>
        <Descriptions.Item label="SID">{user.sid}</Descriptions.Item>
        <Descriptions.Item label="用户名">{user.username}</Descriptions.Item>
        <Descriptions.Item label="显示名">{user.display_name}</Descriptions.Item>
        <Descriptions.Item label="邮箱">{user.email}</Descriptions.Item>
        <Descriptions.Item label="部门">{user.department}</Descriptions.Item>
        <Descriptions.Item label="站点">{user.site_code}</Descriptions.Item>
        <Descriptions.Item label="状态">
          <Tag color={user.is_enabled ? 'green' : 'red'}>{user.is_enabled ? '启用' : '禁用'}</Tag>
        </Descriptions.Item>
      </Descriptions>
    </Drawer>
  )
}