/**
 * MediCareAI Utility Module
 * Common utility functions for the frontend
 */

const Utils = {
    /**
     * Format date to localized string
     * @param {string|Date} date - Date to format
     * @param {Object} options - Intl.DateTimeFormat options
     * @returns {string} Formatted date
     */
    formatDate(date, options = {}) {
        if (!date) return '-';
        
        const d = new Date(date);
        if (isNaN(d.getTime())) return '-';
        
        const defaultOptions = {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            ...options
        };
        
        return d.toLocaleDateString(CONFIG.DATE_FORMAT, defaultOptions);
    },

    /**
     * Format datetime to localized string
     * @param {string|Date} date - Date to format
     * @returns {string} Formatted datetime
     */
    formatDateTime(date) {
        return this.formatDate(date, {
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    /**
     * Format relative time (e.g., "2小时前")
     * @param {string|Date} date 
     * @returns {string}
     */
    formatRelativeTime(date) {
        if (!date) return '-';
        
        const d = new Date(date);
        const now = new Date();
        const diff = now - d;
        
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);
        
        if (minutes < 1) return '刚刚';
        if (minutes < 60) return `${minutes}分钟前`;
        if (hours < 24) return `${hours}小时前`;
        if (days < 30) return `${days}天前`;
        
        return this.formatDate(date);
    },

    /**
     * Truncate text with ellipsis
     * @param {string} text 
     * @param {number} maxLength 
     * @returns {string}
     */
    truncate(text, maxLength = 100) {
        if (!text || text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    },

    /**
     * Format number with commas
     * @param {number} num 
     * @returns {string}
     */
    formatNumber(num) {
        if (num === null || num === undefined) return '-';
        return num.toLocaleString(CONFIG.DATE_FORMAT);
    },

    /**
     * Generate UUID v4
     * @returns {string}
     */
    generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    },

    /**
     * Debounce function execution
     * @param {Function} func 
     * @param {number} wait - Milliseconds to wait
     * @returns {Function}
     */
    debounce(func, wait = 300) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * Show toast notification
     * @param {string} message 
     * @param {string} type - 'success', 'error', 'warning', 'info'
     * @param {number} duration - Milliseconds to show
     */
    showToast(message, type = 'info', duration = 3000) {
        // Remove existing toasts
        const existing = document.querySelector('.toast-notification');
        if (existing) existing.remove();

        const toast = document.createElement('div');
        toast.className = `toast-notification toast-${type}`;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 24px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 10000;
            animation: slideIn 0.3s ease;
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : type === 'warning' ? '#f59e0b' : '#3b82f6'};
        `;
        toast.textContent = message;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    },

    /**
     * Get disease display info
     * @param {Object} disease - Disease object
     * @returns {Object} {name, color, label}
     */
    getDiseaseDisplayInfo(disease) {
        if (!disease) return { name: '-', color: '#666', label: '-' };

        const type = disease.disease_type || 'chronic';
        const color = CONFIG.DISEASE_TYPE_COLORS[type] || '#666';
        const label = CONFIG.DISEASE_TYPE_LABELS[type] || type;
        
        // Prefer Chinese common name
        const name = (disease.common_names && disease.common_names.length > 0)
            ? disease.common_names[0]
            : disease.icd10_name || disease.name || 'Unknown';

        return { name, color, label };
    },

    /**
     * Create disease tag HTML
     * @param {Object} disease 
     * @param {Object} options - Styling options
     * @returns {string} HTML string
     */
    createDiseaseTag(disease, options = {}) {
        const { name, color, label } = this.getDiseaseDisplayInfo(disease);
        const { small = false } = options;

        return `
            <span style="
                display: inline-flex;
                align-items: center;
                gap: ${small ? '2px' : '4px'};
                padding: ${small ? '2px 8px' : '4px 10px'};
                margin: 2px;
                border-radius: ${small ? '10px' : '12px'};
                font-size: ${small ? '11px' : '12px'};
                font-weight: 500;
                background: white;
                border: 1px solid ${color};
                color: ${color};
            ">
                ⚠️ ${name}
            </span>
        `;
    },

    /**
     * Safely parse JSON
     * @param {string} json 
     * @param {*} defaultValue - Default if parsing fails
     * @returns {*}
     */
    safeJSONParse(json, defaultValue = null) {
        try {
            return JSON.parse(json);
        } catch (e) {
            return defaultValue;
        }
    },

    /**
     * Copy text to clipboard
     * @param {string} text 
     * @returns {Promise<boolean>}
     */
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showToast('已复制到剪贴板 | Copied to clipboard', 'success');
            return true;
        } catch (err) {
            this.showToast('复制失败 | Copy failed', 'error');
            return false;
        }
    }
};

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Utils;
}
