import React, { useState, useEffect } from 'react';
import { Layout, Menu, Dropdown, Avatar, message } from 'antd';
import {
  BookOutlined,
  DashboardOutlined,
  SettingOutlined,
  UserOutlined,
  LogoutOutlined
} from '@ant-design/icons';
import BookList from './components/BookList';
import Dashboard from './components/Dashboard';
import Login from './components/Login';
import { isAuthenticated, getUser, logout as authLogout } from './utils/auth';
import './App.css';

const { Header, Content, Sider } = Layout;

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [currentView, setCurrentView] = useState('dashboard');

  useEffect(() => {
    // 检查登录状态
    checkAuthStatus();
  }, []);

  const checkAuthStatus = () => {
    if (isAuthenticated()) {
      const user = getUser();
      setCurrentUser(user);
      setIsLoggedIn(true);
    } else {
      setIsLoggedIn(false);
      setCurrentUser(null);
    }
  };

  const handleLoginSuccess = (user) => {
    setCurrentUser(user);
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    authLogout();
    setIsLoggedIn(false);
    setCurrentUser(null);
    message.success('已退出登录');
  };

  const userMenuItems = [
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: handleLogout
    }
  ];

  // 如果未登录，显示登录页面
  if (!isLoggedIn) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  const menuItems = [
    {
      key: 'dashboard',
      icon: <DashboardOutlined />,
      label: '数据概览'
    },
    {
      key: 'books',
      icon: <BookOutlined />,
      label: '图书管理'
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '系统设置'
    }
  ];

  const renderContent = () => {
    switch (currentView) {
      case 'dashboard':
        return <Dashboard />;
      case 'books':
        return <BookList />;
      case 'settings':
        return (
          <div style={{ padding: 24 }}>
            <h2>系统设置</h2>
            <p>图书管理系统 v2.0.0</p>
            <p>技术栈：React + Ant Design + Python Flask</p>
            <p>已实现用户认证功能</p>
          </div>
        );
      default:
        return <Dashboard />;
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider theme="light" width={200}>
        <div className="logo">
          <h3>📚 图书管理系统</h3>
        </div>
        <Menu
          mode="inline"
          selectedKeys={[currentView]}
          items={menuItems}
          onClick={({ key }) => setCurrentView(key)}
        />
      </Sider>
      <Layout>
        <Header className="header">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>欢迎使用图书管理系统</span>
            <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
              <div className="user-info" style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Avatar icon={<UserOutlined />} />
                <span>{currentUser?.username}</span>
              </div>
            </Dropdown>
          </div>
        </Header>
        <Content className="content">
          {renderContent()}
        </Content>
      </Layout>
    </Layout>
  );
}

export default App;
