import { Form, Input, Button, Card, Alert } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { useAuthStore } from '../stores/authStore'
import client from '../api/client'

interface LoginForm {
  username: string
  password: string
}

export default function LoginPage() {
  const navigate = useNavigate()
  const { setTokens, setUser } = useAuthStore()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (values: LoginForm) => {
    setLoading(true)
    setError(null)

    try {
      const { data } = await client.post('/auth/login', {
        username: values.username,
        password: values.password,
      })

      if (data.code === 0 && data.data) {
        setTokens(data.data.access_token, data.data.refresh_token)
        setUser(data.data.user)
        navigate('/')
      } else {
        setError(data.message || '登录失败')
      }
    } catch (err: any) {
      const errCode = err.response?.data?.data?.code
      if (errCode === 'AUTH_ACCOUNT_LOCKED') {
        setError('账户已被锁定，请联系管理员')
      } else if (errCode === 'AUTH_DC_UNREACHABLE') {
        setError('域控不可达，请检查网络连接')
      } else if (errCode === 'AUTH_PASSWORD_EXPIRED') {
        setError('密码已过期，请联系管理员重置')
      } else {
        setError('用户名或密码错误')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', background: '#f0f2f5' }}>
      <Card title="Htkis-Cloud-ADCS - 登录" style={{ width: 400 }}>
        {error && <Alert message={error} type="error" showIcon style={{ marginBottom: 16 }} />}
        <Form onFinish={handleSubmit}>
          <Form.Item name="username" rules={[{ required: true, message: '请输入用户名' }]}>
            <Input prefix={<UserOutlined />} placeholder="用户名" size="large" />
          </Form.Item>
          <Form.Item name="password" rules={[{ required: true, message: '请输入密码' }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="密码" size="large" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block size="large">
              登录
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  )
}