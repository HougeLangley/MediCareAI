"""
Prometheus Monitoring Setup for MediCareAI
性能监控和指标收集模块
"""

from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging

logger = logging.getLogger(__name__)

# HTTP Request Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

http_request_size_bytes = Histogram(
    'http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint'],
    buckets=[100, 1000, 10000, 100000, 1000000]
)

http_response_size_bytes = Histogram(
    'http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint'],
    buckets=[100, 1000, 10000, 100000, 1000000]
)

# Application Metrics
active_users_gauge = Gauge(
    'active_users_total',
    'Number of active users'
)

ai_requests_total = Counter(
    'ai_requests_total',
    'Total AI diagnosis requests',
    ['status']  # success, error
)

ai_request_duration_seconds = Histogram(
    'ai_request_duration_seconds',
    'AI diagnosis request duration',
    buckets=[1.0, 2.5, 5.0, 10.0, 30.0, 60.0]
)

# Database Metrics
db_connections_gauge = Gauge(
    'db_connections_active',
    'Number of active database connections'
)

db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration',
    ['operation'],  # select, insert, update, delete
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

# Business Metrics
doctor_comments_total = Counter(
    'doctor_comments_total',
    'Total doctor comments',
    ['comment_type']
)

cases_shared_total = Counter(
    'cases_shared_total',
    'Total cases shared',
    ['share_scope']
)

chronic_diseases_tracked = Gauge(
    'chronic_diseases_tracked_total',
    'Number of chronic disease conditions tracked'
)

# System Info
app_info = Info('medicareai_app', 'MediCareAI application information')


class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Middleware to collect Prometheus metrics for all HTTP requests
    """
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Get request details
        method = request.method
        endpoint = request.url.path
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Record metrics
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()
            
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            # Log slow requests
            if duration > 5.0:
                logger.warning(f"Slow request: {method} {endpoint} took {duration:.2f}s")
            
            return response
            
        except Exception as e:
            # Record error
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=500
            ).inc()
            raise


def track_ai_request(duration: float, success: bool = True):
    """Track AI diagnosis request metrics"""
    status = 'success' if success else 'error'
    ai_requests_total.labels(status=status).inc()
    ai_request_duration_seconds.observe(duration)


def track_db_query(operation: str, duration: float):
    """Track database query metrics"""
    db_query_duration_seconds.labels(operation=operation).observe(duration)


def track_doctor_comment(comment_type: str):
    """Track doctor comment metrics"""
    doctor_comments_total.labels(comment_type=comment_type).inc()


def track_case_shared(share_scope: str):
    """Track case sharing metrics"""
    cases_shared_total.labels(share_scope=share_scope).inc()


def update_active_users(count: int):
    """Update active users gauge"""
    active_users_gauge.set(count)


def update_chronic_diseases(count: int):
    """Update chronic diseases gauge"""
    chronic_diseases_tracked.set(count)


def set_app_info(version: str, environment: str):
    """Set application info"""
    app_info.info({
        'version': version,
        'environment': environment
    })


def get_metrics():
    """Get Prometheus metrics in text format"""
    return generate_latest()
