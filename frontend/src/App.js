import React, { useState } from 'react';
import { Layout, Menu } from 'antd';
import {
  BookOutlined,
  DashboardOutlined,
  SettingOutlined
} from '@ant-design/icons';
import BookList from './components/BookList';
import Dashboard from './components/Dashboard';
import './App.css';

const { Header, Content, Sider } = Layout;

function App() {
  const [currentView, setCurrentView] = useState('dashboard');

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
            <p>图书管理系统 v1.0.0</p>
            <p>技术栈：React + Ant Design + Python Flask</p>
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
          <span>欢迎使用图书管理系统</span>
        </Header>
        <Content className="content">
          {renderContent()}
        </Content>
      </Layout>
    </Layout>
  );
}

export default App;
