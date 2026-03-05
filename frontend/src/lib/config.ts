// 全局配置文件
export const CONFIG = {
  // API 配置
  API_BASE: '',  // 使用相对路径，通过 Nginx 代理访问 API
  API_VERSION: '/api/v1',
  
  // 请求配置
  REQUEST_TIMEOUT: 30000, // 30秒
  
  // 存储键名
  TOKEN_KEY: 'medicare_token',
  REFRESH_TOKEN_KEY: 'medicare_refresh_token',
  USER_KEY: 'medicare_user',
  
  // 分页配置
  DEFAULT_PAGE_SIZE: 10,
  MAX_PAGE_SIZE: 100,
  
  // 文件上传配置
  MAX_FILE_SIZE: 200 * 1024 * 1024, // 200MB
  ALLOWED_FILE_TYPES: [
    'image/jpeg',
    'image/png',
    'image/gif',
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  ],
  
  // 应用信息
  APP_NAME: 'MediCareAI',
  APP_VERSION: '1.0.0',
};
