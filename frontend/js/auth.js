/**
 * MediCareAI Authentication Module
 * Token management and authentication utilities
 */

const Auth = {
    /**
     * Get access token from localStorage
     * @returns {string|null} Access token or null
     */
    getToken() {
        return localStorage.getItem(CONFIG.TOKEN_KEY);
    },

    /**
     * Get refresh token from localStorage
     * @returns {string|null} Refresh token or null
     */
    getRefreshToken() {
        return localStorage.getItem(CONFIG.REFRESH_TOKEN_KEY);
    },

    /**
     * Set tokens in localStorage
     * @param {string} accessToken 
     * @param {string} refreshToken 
     */
    setTokens(accessToken, refreshToken) {
        localStorage.setItem(CONFIG.TOKEN_KEY, accessToken);
        if (refreshToken) {
            localStorage.setItem(CONFIG.REFRESH_TOKEN_KEY, refreshToken);
        }
    },

    /**
     * Clear all authentication data
     */
    clear() {
        localStorage.removeItem(CONFIG.TOKEN_KEY);
        localStorage.removeItem(CONFIG.REFRESH_TOKEN_KEY);
        localStorage.removeItem('user_info');
    },

    /**
     * Check if user is authenticated
     * @returns {boolean}
     */
    isAuthenticated() {
        return !!this.getToken();
    },

    /**
     * Get Authorization header for API requests
     * @returns {Object} Header object with Authorization
     */
    getAuthHeader() {
        const token = this.getToken();
        return token ? { 'Authorization': `Bearer ${token}` } : {};
    },

    /**
     * Refresh access token using refresh token
     * @returns {Promise<boolean>} True if refresh successful
     */
    async refreshToken() {
        const refreshToken = this.getRefreshToken();
        if (!refreshToken) {
            return false;
        }

        try {
            const response = await fetch(`${CONFIG.API_BASE}${CONFIG.API_VERSION}/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ refresh_token: refreshToken })
            });

            if (response.ok) {
                const data = await response.json();
                this.setTokens(data.access_token, data.refresh_token);
                return true;
            }
        } catch (error) {
            console.error('Token refresh failed:', error);
        }

        return false;
    },

    /**
     * Redirect to login page if not authenticated
     */
    requireAuth() {
        if (!this.isAuthenticated()) {
            window.location.href = '/login.html';
        }
    },

    /**
     * Logout user and clear session
     */
    logout() {
        this.clear();
        window.location.href = '/login.html';
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Auth;
}
