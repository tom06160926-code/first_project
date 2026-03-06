/**
 * 认证工具模块
 * 处理 token 存储和用户认证状态
 */

const TOKEN_KEY = 'book_management_token';
const USER_KEY = 'book_management_user';

/**
 * 保存 token 到 localStorage
 */
export const setToken = (token) => {
  localStorage.setItem(TOKEN_KEY, token);
};

/**
 * 从 localStorage 获取 token
 */
export const getToken = () => {
  return localStorage.getItem(TOKEN_KEY);
};

/**
 * 删除 token
 */
export const removeToken = () => {
  localStorage.removeItem(TOKEN_KEY);
};

/**
 * 保存用户信息到 localStorage
 */
export const setUser = (user) => {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
};

/**
 * 从 localStorage 获取用户信息
 */
export const getUser = () => {
  const userStr = localStorage.getItem(USER_KEY);
  return userStr ? JSON.parse(userStr) : null;
};

/**
 * 删除用户信息
 */
export const removeUser = () => {
  localStorage.removeItem(USER_KEY);
};

/**
 * 检查用户是否已登录
 */
export const isAuthenticated = () => {
  const token = getToken();
  const user = getUser();
  return !!(token && user);
};

/**
 * 登录 - 保存 token 和用户信息
 */
export const login = (token, user) => {
  setToken(token);
  setUser(user);
};

/**
 * 登出 - 清除 token 和用户信息
 */
export const logout = () => {
  removeToken();
  removeUser();
};

/**
 * 获取认证头
 */
export const getAuthHeader = () => {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
};
