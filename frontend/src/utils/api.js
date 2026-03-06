/**
 * API 客户端配置
 * 配置 Axios 拦截器处理认证
 */

import axios from 'axios';
import { getToken, logout } from './auth';

// 创建 Axios 实例
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 自动添加 token
api.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 统一错误处理
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // 处理 401 未授权错误
    if (error.response) {
      if (error.response.status === 401) {
        // Token 过期或无效，清除登录状态并跳转登录页
        logout();
        window.location.href = '/login';
      }
      return Promise.reject({
        message: error.response.data?.error || '请求失败',
        status: error.response.status,
        data: error.response.data,
      });
    } else if (error.request) {
      // 请求已发出但没有收到响应
      return Promise.reject({
        message: '网络错误，请检查网络连接',
        status: null,
      });
    } else {
      // 请求配置出错
      return Promise.reject({
        message: '请求配置错误',
        status: null,
      });
    }
  }
);

export default api;
