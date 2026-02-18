/**
 * MediCareAI Error Messages
 * Centralized bilingual error messages (English | 中文)
 */

const ErrorMessages = {
    // Authentication Errors
    AUTH_INVALID_CREDENTIALS: "Invalid credentials | 邮箱或密码不正确",
    AUTH_TOKEN_EXPIRED: "Token expired | 登录已过期",
    AUTH_UNAUTHORIZED: "Unauthorized | 未授权",
    AUTH_FORBIDDEN: "Access denied | 访问被拒绝",
    
    // Resource Not Found
    NOT_FOUND: "Resource not found | 资源未找到",
    CASE_NOT_FOUND: "Case not found | 病例未找到",
    USER_NOT_FOUND: "User not found | 用户未找到",
    DOCTOR_NOT_FOUND: "Doctor not found | 医生未找到",
    PATIENT_NOT_FOUND: "Patient not found | 患者未找到",
    COMMENT_NOT_FOUND: "Comment not found | 评论未找到",
    MENTION_NOT_FOUND: "Mention not found | 提及记录未找到",
    DISEASE_NOT_FOUND: "Disease not found | 疾病未找到",
    
    // Validation Errors
    VALIDATION_ERROR: "Validation error | 验证错误",
    INVALID_INPUT: "Invalid input | 输入无效",
    MISSING_FIELD: "Missing required field | 缺少必填字段",
    INVALID_DATE: "Invalid date format | 日期格式无效",
    
    // Permission Errors
    PERMISSION_DENIED: "Permission denied | 权限不足",
    NOT_OWNER: "Can only modify your own resources | 只能修改自己的资源",
    CASE_NOT_VISIBLE: "Case not visible to you | 病例对您不可见",
    
    // Server Errors
    SERVER_ERROR: "Internal server error | 服务器内部错误",
    DATABASE_ERROR: "Database error | 数据库错误",
    SERVICE_UNAVAILABLE: "Service temporarily unavailable | 服务暂时不可用",
    
    // Success Messages
    SUCCESS_CREATE: "Created successfully | 创建成功",
    SUCCESS_UPDATE: "Updated successfully | 更新成功",
    SUCCESS_DELETE: "Deleted successfully | 删除成功",
    SUCCESS_EXPORT: "Exported successfully | 导出成功",
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ErrorMessages;
}
