import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic } from 'antd';
import {
  BookOutlined,
  DatabaseOutlined,
  AppstoreOutlined
} from '@ant-design/icons';
import api from '../utils/api';

function Dashboard() {
  const [stats, setStats] = useState({
    total_books: 0,
    total_stock: 0,
    categories: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await api.get('/stats');
      setStats(response.data);
    } catch (error) {
      console.error('获取统计数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>数据概览</h2>
      <Row gutter={16} style={{ marginTop: 24 }}>
        <Col span={8}>
          <Card loading={loading}>
            <Statistic
              title="图书总数"
              value={stats.total_books}
              prefix={<BookOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card loading={loading}>
            <Statistic
              title="库存总量"
              value={stats.total_stock}
              prefix={<DatabaseOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card loading={loading}>
            <Statistic
              title="分类数量"
              value={stats.categories}
              prefix={<AppstoreOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default Dashboard;
