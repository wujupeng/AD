import { Card, Form, Input, Button, Result, Descriptions } from 'antd'
import { useState } from 'react'
import client from '../api/client'

export default function PermissionCheckPage() {
  const [form] = Form.useForm()
  const [result, setResult] = useState<{ allowed: boolean; reason: string; groups: string[] } | null>(null)
  const [loading, setLoading] = useState(false)

  const handleCheck = async (values: { user_sid: string; resource: string; action: string }) => {
    setLoading(true)
    try {
      const { data } = await client.get('/permissions/check', { params: values })
      if (data.code === 0 && data.data) {
        setResult(data.data)
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card title="权限检查">
      <Form form={form} onFinish={handleCheck} layout="inline">
        <Form.Item name="user_sid" rules={[{ required: true, message: '请输入用户SID' }]}>
          <Input placeholder="用户 SID" />
        </Form.Item>
        <Form.Item name="resource" rules={[{ required: true, message: '请输入资源' }]}>
          <Input placeholder="资源" />
        </Form.Item>
        <Form.Item name="action" rules={[{ required: true, message: '请输入操作' }]}>
          <Input placeholder="操作" />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading}>检查</Button>
        </Form.Item>
      </Form>
      {result && (
        <Result
          status={result.allowed ? 'success' : 'error'}
          title={result.allowed ? '允许' : '拒绝'}
          subTitle={result.reason}
          extra={
            result.groups.length > 0 && (
              <Descriptions column={1}>
                <Descriptions.Item label="授权组">{result.groups.join(', ')}</Descriptions.Item>
              </Descriptions>
            )
          }
        />
      )}
    </Card>
  )
}