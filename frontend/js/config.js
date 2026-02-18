/**
 * MediCareAI Frontend Configuration
 * API and application configuration settings
 */

const CONFIG = {
    // API Base URL - automatically detects localhost vs production
    API_BASE: window.location.hostname === 'localhost' 
        ? 'http://localhost:8000' 
        : '',
    
    // API Version
    API_VERSION: '/api/v1',
    
    // Token storage keys
    TOKEN_KEY: 'access_token',
    REFRESH_TOKEN_KEY: 'refresh_token',
    
    // Request timeout (milliseconds)
    REQUEST_TIMEOUT: 30000,
    
    // Pagination defaults
    DEFAULT_PAGE_SIZE: 20,
    
    // Date format
    DATE_FORMAT: 'zh-CN',
    
    // Chronic disease type colors
    DISEASE_TYPE_COLORS: {
        special: '#dc3545',      // 特殊病 - Red
        chronic: '#007bff',      // 慢性病 - Blue
        both: '#6f42c1'          // 两者兼具 - Purple
    },
    
    DISEASE_TYPE_LABELS: {
        special: '特殊病',
        chronic: '慢性病',
        both: '特殊病+慢性病'
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}
