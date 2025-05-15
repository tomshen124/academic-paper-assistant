import { request } from '../../utils/request';
import type { AxiosResponse } from 'axios';

/**
 * 登录请求参数
 */
export interface LoginRequest {
  username: string;
  password: string;
}

/**
 * 登录响应
 */
export interface LoginResponse {
  access_token: string;
  token_type: string;
}

/**
 * 刷新令牌请求参数
 */
export interface RefreshTokenRequest {
  token: string;
}

/**
 * 用户信息
 */
export interface UserInfo {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string | null;
}

/**
 * 登录
 * @param data 登录参数
 * @returns 登录响应
 */
export function login(data: LoginRequest): Promise<LoginResponse> {
  return request({
    url: '/auth/login/json',
    method: 'post',
    data
  });
}

/**
 * 刷新令牌
 * @param token 当前令牌
 * @returns 新令牌
 */
export function refreshToken(token: string): Promise<LoginResponse> {
  return request({
    url: '/auth/refresh',
    method: 'post',
    data: { token }
  });
}

/**
 * 获取当前用户信息
 * @returns 用户信息
 */
export function getUserInfo(): Promise<UserInfo> {
  return request({
    url: '/users/me',
    method: 'get'
  });
}

/**
 * 注册用户
 * @param data 注册参数
 * @returns 用户信息
 */
export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export function register(data: RegisterRequest): Promise<UserInfo> {
  return request({
    url: '/users/register',
    method: 'post',
    data
  });
}
