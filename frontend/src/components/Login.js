/**
 * 登录/注册组件
 * 使用 Ant Design 组件
 */

import React, { useState } from 'react';
import { Form, Input, Button, Tabs, message, Card } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import api from '../utils/api';
import { login as authLogin } from '../utils/auth';
import './Login.css';

function Login({ onLoginSuccess }) {
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('login');

  // 登录处理
  const handleLogin = async (values) => {
    setLoading(true);
    try {
      const response = await api.post('/auth/login', {
        username: values.username,
        password: values.password,
      });

      const { token, user } = response.data;
      authLogin(token, user);

      message.success('登录成功！');
      if (onLoginSuccess) {
        onLoginSuccess(user);
      }
    } catch (error) {
      message.error(error.message || '登录失败，请检查用户名和密码');
    } finally {
      setLoading(false);
    }
  };

  // 注册处理
  const handleRegister = async (values) => {
    setLoading(true);
    try {
      const response = await api.post('/auth/register', {
        username: values.username,
        email: values.email,
        password: values.password,
      });

      const { token, user } = response.data;
      authLogin(token, user);

      message.success('注册成功！已自动登录');
      if (onLoginSuccess) {
        onLoginSuccess(user);
      }
    } catch (error) {
      const errorMsg = error.data?.error || error.message || '注册失败';
      message.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-background">
        <div className="login-content">
          <Card className="login-card">
            <div className="login-header">
              <h1>📚 图书管理系统</h1>
              <p>欢迎使用图书管理系统</p>
            </div>

            <Tabs
              activeKey={activeTab}
              onChange={setActiveTab}
              centered
              items={[
                {
                  key: 'login',
                  label: '登录',
                  children: (
                    <Form
                      name="login"
                      onFinish={handleLogin}
                      autoComplete="off"
                      layout="vertical"
                    >
                      <Form.Item
                        name="username"
                        rules={[{ required: true, message: '请输入用户名' }]}
                      >
                        <Input
                          prefix={<UserOutlined />}
                          placeholder="用户名"
                          size="large"
                        />
                      </Form.Item>

                      <Form.Item
                        name="password"
                        rules={[{ required: true, message: '请输入密码' }]}
                      >
                        <Input.Password
                          prefix={<LockOutlined />}
                          placeholder="密码"
                          size="large"
                        />
                      </Form.Item>

                      <Form.Item>
                        <Button
                          type="primary"
                          htmlType="submit"
                          loading={loading}
                          size="large"
                          block
                        >
                          登录
                        </Button>
                      </Form.Item>
                    </Form>
                  ),
                },
                {
                  key: 'register',
                  label: '注册',
                  children: (
                    <Form
                      name="register"
                      onFinish={handleRegister}
                      autoComplete="off"
                      layout="vertical"
                    >
                      <Form.Item
                        name="username"
                        rules={[
                          { required: true, message: '请输入用户名' },
                          { min: 3, message: '用户名至少3个字符' },
                          { max: 20, message: '用户名最多20个字符' },
                        ]}
                      >
                        <Input
                          prefix={<UserOutlined />}
                          placeholder="用户名"
                          size="large"
                        />
                      </Form.Item>

                      <Form.Item
                        name="email"
                        rules={[
                          { required: true, message: '请输入邮箱' },
                          { type: 'email', message: '请输入有效的邮箱地址' },
                        ]}
                      >
                        <Input
                          prefix={<MailOutlined />}
                          placeholder="邮箱"
                          size="large"
                        />
                      </Form.Item>

                      <Form.Item
                        name="password"
                        dependencies={['confirm']}
                        rules={[
                          { required: true, message: '请输入密码' },
                          { min: 6, message: '密码至少6个字符' },
                        ]}
                      >
                        <Input.Password
                          prefix={<LockOutlined />}
                          placeholder="密码"
                          size="large"
                        />
                      </Form.Item>

                      <Form.Item
                        name="confirm"
                        dependencies={['password']}
                        rules={[
                          { required: true, message: '请确认密码' },
                          ({ getFieldValue }) => ({
                            validator(_, value) {
                              if (!value || getFieldValue('password') === value) {
                                return Promise.resolve();
                              }
                              return Promise.reject(new Error('两次输入的密码不一致'));
                            },
                          }),
                        ]}
                      >
                        <Input.Password
                          prefix={<LockOutlined />}
                          placeholder="确认密码"
                          size="large"
                        />
                      </Form.Item>

                      <Form.Item>
                        <Button
                          type="primary"
                          htmlType="submit"
                          loading={loading}
                          size="large"
                          block
                        >
                          注册
                        </Button>
                      </Form.Item>
                    </Form>
                  ),
                },
              ]}
            />
          </Card>

          <div className="login-footer">
            <p>默认管理员账户: admin / admin123</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;
