import React, { useState, useEffect } from 'react';
import {
  Table, Button, Space, Modal, Form, Input, InputNumber,
  DatePicker, Select, Popconfirm, message, Card, Row, Col
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SearchOutlined
} from '@ant-design/icons';
import api from '../utils/api';
import moment from 'moment';

function BookList() {
  const [books, setBooks] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingBook, setEditingBook] = useState(null);
  const [form] = Form.useForm();
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  });
  const [searchParams, setSearchParams] = useState({
    search: '',
    category: ''
  });

  useEffect(() => {
    fetchBooks();
    fetchCategories();
  }, [pagination.current, pagination.pageSize, searchParams]);

  const fetchBooks = async () => {
    setLoading(true);
    try {
      const response = await api.get('/books', {
        params: {
          page: pagination.current,
          per_page: pagination.pageSize,
          ...searchParams
        }
      });
      setBooks(response.data.items);
      setPagination({
        ...pagination,
        total: response.data.total
      });
    } catch (error) {
      message.error('获取图书列表失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await api.get('/categories');
      setCategories(response.data);
    } catch (error) {
      console.error('获取分类失败:', error);
    }
  };

  const handleAdd = () => {
    setEditingBook(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record) => {
    setEditingBook(record);
    form.setFieldsValue({
      ...record,
      publish_date: record.publish_date ? moment(record.publish_date) : null
    });
    setModalVisible(true);
  };

  const handleDelete = async (id) => {
    try {
      await api.delete(`/books/${id}`);
      message.success('删除成功');
      fetchBooks();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleSubmit = async (values) => {
    try {
      const data = {
        ...values,
        publish_date: values.publish_date ? values.publish_date.format('YYYY-MM-DD') : null
      };

      if (editingBook) {
        await api.put(`/books/${editingBook.id}`, data);
        message.success('更新成功');
      } else {
        await api.post('/books', data);
        message.success('添加成功');
      }

      setModalVisible(false);
      fetchBooks();
    } catch (error) {
      message.error(editingBook ? '更新失败' : '添加失败');
    }
  };

  const handleSearch = (values) => {
    setSearchParams(values);
    setPagination({ ...pagination, current: 1 });
  };

  const columns = [
    {
      title: '书名',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true
    },
    {
      title: '作者',
      dataIndex: 'author',
      key: 'author',
      width: 120
    },
    {
      title: 'ISBN',
      dataIndex: 'isbn',
      key: 'isbn',
      width: 150
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 100
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      width: 100,
      render: (price) => `¥${price?.toFixed(2) || '0.00'}`
    },
    {
      title: '库存',
      dataIndex: 'stock',
      key: 'stock',
      width: 80
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_, record) => (
        <Space size="small">
          <Button
            type="primary"
            icon={<EditOutlined />}
            size="small"
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定删除?"
            onConfirm={() => handleDelete(record.id)}
          >
            <Button
              danger
              icon={<DeleteOutlined />}
              size="small"
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      )
    }
  ];

  return (
    <div>
      <h2>图书管理</h2>

      <Card style={{ marginBottom: 24 }}>
        <Form layout="inline" onFinish={handleSearch}>
          <Form.Item name="search" label="搜索">
            <Input
              placeholder="书名/作者/ISBN"
              prefix={<SearchOutlined />}
              allowClear
            />
          </Form.Item>
          <Form.Item name="category" label="分类">
            <Select
              placeholder="选择分类"
              allowClear
              style={{ width: 120 }}
            >
              {categories.map(cat => (
                <Select.Option key={cat} value={cat}>{cat}</Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit">
              查询
            </Button>
          </Form.Item>
        </Form>
      </Card>

      <div style={{ marginBottom: 16 }}>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          添加图书
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={books}
        rowKey="id"
        loading={loading}
        pagination={{
          ...pagination,
          showSizeChanger: true,
          showTotal: (total) => `共 ${total} 条`
        }}
        onChange={(p) => setPagination({ ...pagination, ...p })}
      />

      <Modal
        title={editingBook ? '编辑图书' : '添加图书'}
        open={modalVisible}
        onOk={() => form.submit()}
        onCancel={() => setModalVisible(false)}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="title"
                label="书名"
                rules={[{ required: true, message: '请输入书名' }]}
              >
                <Input placeholder="请输入书名" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="author"
                label="作者"
                rules={[{ required: true, message: '请输入作者' }]}
              >
                <Input placeholder="请输入作者" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="isbn"
                label="ISBN"
              >
                <Input placeholder="请输入ISBN" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="publisher"
                label="出版社"
              >
                <Input placeholder="请输入出版社" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="category"
                label="分类"
              >
                <Select placeholder="选择分类" allowClear>
                  {categories.map(cat => (
                    <Select.Option key={cat} value={cat}>{cat}</Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="publish_date"
                label="出版日期"
              >
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="price"
                label="价格"
              >
                <InputNumber
                  style={{ width: '100%' }}
                  min={0}
                  precision={2}
                  prefix="¥"
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="stock"
                label="库存"
              >
                <InputNumber
                  style={{ width: '100%' }}
                  min={0}
                  precision={0}
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="description"
            label="简介"
          >
            <Input.TextArea rows={3} placeholder="请输入图书简介" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

export default BookList;
