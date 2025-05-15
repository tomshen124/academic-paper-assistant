import { refreshToken } from '@/api/modules/auth';
import { jwtDecode } from 'jwt-decode'

interface JwtPayload {
  exp: number;
  sub: string;
  [key: string]: any;
}

/**
 * 检查令牌是否过期或即将过期
 * @param token JWT令牌
 * @param minutesThreshold 过期前多少分钟开始刷新（默认5分钟）
 * @returns 是否过期或即将过期
 */
export function isTokenExpired(token: string, minutesThreshold: number = 5): boolean {
  try {
    const decoded = jwtDecode<JwtPayload>(token);
    if (!decoded.exp) return true;

    // 计算过期时间（毫秒）
    const expirationTime = decoded.exp * 1000;
    // 当前时间加上阈值（毫秒）
    const currentTime = Date.now() + minutesThreshold * 60 * 1000;

    return currentTime >= expirationTime;
  } catch (error) {
    console.error('解析令牌失败:', error);
    return true; // 如果解析失败，视为过期
  }
}

/**
 * 如果需要，刷新令牌
 * @param token 当前令牌
 * @returns 新令牌或原令牌
 */
export async function refreshTokenIfNeeded(token: string): Promise<string> {
  try {
    // 检查令牌是否即将过期
    if (isTokenExpired(token)) {
      console.log('令牌即将过期，正在刷新...');
      const response = await refreshToken(token);
      const newToken = response.access_token;

      // 保存新令牌
      localStorage.setItem('token', newToken);
      console.log('令牌刷新成功');

      return newToken;
    }

    return token;
  } catch (error) {
    console.error('刷新令牌失败:', error);
    return token; // 如果刷新失败，返回原令牌
  }
}

/**
 * 获取令牌中的用户名
 * @param token JWT令牌
 * @returns 用户名
 */
export function getUsernameFromToken(token: string): string | null {
  try {
    const decoded = jwtDecode<JwtPayload>(token);
    return decoded.sub || null;
  } catch (error) {
    console.error('从令牌获取用户名失败:', error);
    return null;
  }
}
