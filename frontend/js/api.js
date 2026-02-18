/**
 * MediCareAI API Module
 * Unified API request wrapper with error handling
 */

const API = {
    /**
     * Build full API URL
     * @param {string} endpoint - API endpoint path
     * @returns {string} Full URL
     */
    buildUrl(endpoint) {
        return `${CONFIG.API_BASE}${CONFIG.API_VERSION}${endpoint}`;
    },

    /**
     * Make API request with automatic auth and error handling
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Fetch options
     * @returns {Promise<Object>} Response data
     */
    async request(endpoint, options = {}) {
        const url = this.buildUrl(endpoint);
        
        // Default headers
        const headers = {
            'Content-Type': 'application/json',
            ...Auth.getAuthHeader(),
            ...options.headers
        };

        try {
            const response = await fetch(url, {
                ...options,
                headers,
                timeout: CONFIG.REQUEST_TIMEOUT
            });

            // Handle 401 - try to refresh token
            if (response.status === 401) {
                const refreshed = await Auth.refreshToken();
                if (refreshed) {
                    // Retry with new token
                    headers['Authorization'] = `Bearer ${Auth.getToken()}`;
                    const retryResponse = await fetch(url, {
                        ...options,
                        headers,
                        timeout: CONFIG.REQUEST_TIMEOUT
                    });
                    return this.handleResponse(retryResponse);
                } else {
                    Auth.logout();
                    throw new Error('Session expired | 会话已过期');
                }
            }

            return this.handleResponse(response);
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    },

    /**
     * Handle API response
     * @param {Response} response - Fetch response
     * @returns {Promise<Object>} Parsed response
     */
    async handleResponse(response) {
        if (!response.ok) {
            const error = await response.json().catch(() => ({
                detail: 'Request failed | 请求失败'
            }));
            throw new Error(error.detail || `HTTP ${response.status}`);
        }

        // Handle empty responses
        if (response.status === 204) {
            return null;
        }

        return response.json();
    },

    /**
     * GET request
     * @param {string} endpoint 
     * @param {Object} params - Query parameters
     * @returns {Promise<Object>}
     */
    async get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        return this.request(url, { method: 'GET' });
    },

    /**
     * POST request
     * @param {string} endpoint 
     * @param {Object} data - Request body
     * @returns {Promise<Object>}
     */
    async post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    /**
     * PUT request
     * @param {string} endpoint 
     * @param {Object} data - Request body
     * @returns {Promise<Object>}
     */
    async put(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    /**
     * DELETE request
     * @param {string} endpoint 
     * @returns {Promise<Object>}
     */
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    },

    /**
     * Upload file
     * @param {string} endpoint 
     * @param {FormData} formData 
     * @param {Function} onProgress - Progress callback
     * @returns {Promise<Object>}
     */
    async upload(endpoint, formData, onProgress = null) {
        const url = this.buildUrl(endpoint);
        
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            
            if (onProgress) {
                xhr.upload.addEventListener('progress', onProgress);
            }

            xhr.addEventListener('load', () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    resolve(JSON.parse(xhr.responseText));
                } else {
                    reject(new Error(`Upload failed | 上传失败: ${xhr.statusText}`));
                }
            });

            xhr.addEventListener('error', () => {
                reject(new Error('Upload failed | 上传失败'));
            });

            xhr.open('POST', url);
            xhr.setRequestHeader('Authorization', `Bearer ${Auth.getToken()}`);
            xhr.send(formData);
        });
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = API;
}
