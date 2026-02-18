/**
 * MediCareAI Monitoring Module
 * Prometheus metrics collection and monitoring utilities
 */

const Monitoring = {
    /**
     * Track API call metrics
     * @param {string} endpoint - API endpoint
     * @param {string} method - HTTP method
     * @param {number} duration - Request duration in ms
     * @param {number} status - HTTP status code
     */
    trackAPICall(endpoint, method, duration, status) {
        // In a real implementation, this would send metrics to Prometheus
        // For now, we log to console in development
        if (CONFIG.DEBUG) {
            console.log(`[API] ${method} ${endpoint} - ${status} (${duration}ms)`);
        }
        
        // Store in local metrics for debugging
        if (!window._apiMetrics) window._apiMetrics = [];
        window._apiMetrics.push({
            endpoint,
            method,
            duration,
            status,
            timestamp: new Date().toISOString()
        });
        
        // Keep only last 100 entries
        if (window._apiMetrics.length > 100) {
            window._apiMetrics.shift();
        }
    },

    /**
     * Track page load performance
     */
    trackPageLoad() {
        if (window.performance) {
            window.addEventListener('load', () => {
                setTimeout(() => {
                    const perfData = window.performance.timing;
                    const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
                    
                    if (CONFIG.DEBUG) {
                        console.log(`[Performance] Page load time: ${pageLoadTime}ms`);
                    }
                    
                    // Send to backend monitoring endpoint
                    this.sendMetric('page_load_time', pageLoadTime, {
                        page: window.location.pathname
                    });
                }, 0);
            });
        }
    },

    /**
     * Track JavaScript errors
     */
    trackErrors() {
        window.addEventListener('error', (event) => {
            this.sendMetric('js_error', 1, {
                message: event.message,
                filename: event.filename,
                lineno: event.lineno
            });
        });
        
        window.addEventListener('unhandledrejection', (event) => {
            this.sendMetric('js_promise_rejection', 1, {
                reason: event.reason?.toString() || 'Unknown'
            });
        });
    },

    /**
     * Send metric to backend
     * @param {string} metricName 
     * @param {number} value 
     * @param {Object} labels 
     */
    async sendMetric(metricName, value, labels = {}) {
        try {
            await API.post('/monitoring/metrics', {
                metric: metricName,
                value,
                labels,
                timestamp: new Date().toISOString()
            });
        } catch (error) {
            // Silently fail - monitoring should not break the app
            console.debug('Failed to send metric:', error);
        }
    },

    /**
     * Get API metrics summary
     * @returns {Object} Metrics summary
     */
    getAPIMetrics() {
        if (!window._apiMetrics) return {};
        
        const metrics = window._apiMetrics;
        const total = metrics.length;
        
        if (total === 0) return {};
        
        const byStatus = {};
        const byEndpoint = {};
        let totalDuration = 0;
        
        metrics.forEach(m => {
            // By status code
            byStatus[m.status] = (byStatus[m.status] || 0) + 1;
            
            // By endpoint
            byEndpoint[m.endpoint] = byEndpoint[m.endpoint] || { count: 0, totalDuration: 0 };
            byEndpoint[m.endpoint].count++;
            byEndpoint[m.endpoint].totalDuration += m.duration;
            
            totalDuration += m.duration;
        });
        
        return {
            total,
            averageDuration: Math.round(totalDuration / total),
            byStatus,
            byEndpoint: Object.fromEntries(
                Object.entries(byEndpoint).map(([k, v]) => [
                    k,
                    { count: v.count, avgDuration: Math.round(v.totalDuration / v.count) }
                ])
            )
        };
    },

    /**
     * Display metrics in console (for debugging)
     */
    showMetrics() {
        const metrics = this.getAPIMetrics();
        console.table(metrics.byStatus);
        console.table(metrics.byEndpoint);
    }
};

// Auto-track page loads
Monitoring.trackPageLoad();
Monitoring.trackErrors();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Monitoring;
}
