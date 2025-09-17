# Analytics API

The Analytics API provides comprehensive SMS usage analytics, cost analysis, and performance monitoring capabilities for both individual users and system administrators.

## Base URL

```
/api/v1/analytics
```

## Authentication

All endpoints require authentication via JWT token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

## Rate Limiting

- **User endpoints**: 100 requests per minute
- **Admin endpoints**: 200 requests per minute

## User Analytics Endpoints

### Get User SMS Analytics

Get comprehensive SMS usage analytics for the current user.

**Endpoint**: `GET /me/sms-analytics`

**Query Parameters**:

- `time_range` (string, optional): Time range for analytics. Options: `7d`, `30d`, `90d`, `1y`. Default: `30d`

**Response**:

```json
{
  "user_id": 123,
  "time_range": "30d",
  "usage_summary": {
    "total_messages": 150,
    "inbound_messages": 75,
    "outbound_messages": 75,
    "success_rate": 98.5,
    "average_processing_time_ms": 250
  },
  "usage_trends": {
    "daily_breakdown": [
      {
        "date": "2024-01-01",
        "inbound": 3,
        "outbound": 2,
        "total": 5
      }
    ],
    "hourly_patterns": {
      "peak_hours": [9, 10, 11, 14, 15, 16],
      "average_per_hour": 2.1
    }
  },
  "performance_metrics": {
    "successful_messages": 148,
    "failed_messages": 2,
    "success_rate": 98.5,
    "processing_time_metrics": {
      "average_ms": 250,
      "minimum_ms": 120,
      "maximum_ms": 800,
      "p95_ms": 450
    }
  },
  "message_breakdown": {
    "by_type": {
      "sms": 140,
      "mms": 10
    },
    "by_status": {
      "delivered": 148,
      "failed": 2,
      "pending": 0
    }
  },
  "generated_at": "2024-01-15T10:30:00Z"
}
```

**Required Permissions**: `user:read_sms_analytics`

### Get User SMS Costs

Get detailed cost analysis for the current user's SMS usage.

**Endpoint**: `GET /me/sms-costs`

**Query Parameters**:

- `time_range` (string, optional): Time range for cost analysis. Options: `7d`, `30d`, `90d`, `1y`. Default: `30d`

**Response**:

```json
{
  "user_id": 123,
  "time_range": "30d",
  "cost_breakdown": {
    "total_cost_usd": 12.5,
    "inbound_cost_usd": 6.25,
    "outbound_cost_usd": 5.75,
    "mms_cost_usd": 0.5,
    "monthly_number_cost_usd": 1.0,
    "total_with_monthly_fees": 13.5,
    "cost_per_message": 0.083
  },
  "cost_trends": {
    "daily_costs": [
      {
        "date": "2024-01-01",
        "cost_usd": 0.45
      }
    ],
    "monthly_projection": 13.5,
    "cost_growth_rate": 0.05
  },
  "optimization_tips": [
    {
      "category": "usage",
      "tip": "Consider consolidating multiple short messages into fewer longer messages",
      "potential_savings": 0.25
    },
    {
      "category": "timing",
      "tip": "Avoid sending messages during peak hours to reduce processing costs",
      "potential_savings": 0.15
    }
  ],
  "generated_at": "2024-01-15T10:30:00Z"
}
```

**Required Permissions**: `user:read_sms_costs`

### Download User Usage Report

Download a comprehensive SMS usage report in CSV or JSON format.

**Endpoint**: `GET /me/sms-usage-report`

**Query Parameters**:

- `format` (string, optional): Report format. Options: `csv`, `json`. Default: `csv`
- `time_range` (string, optional): Time range for report. Options: `7d`, `30d`, `90d`, `1y`. Default: `30d`

**Response**:

- **CSV Format**: Returns a CSV file with detailed usage, performance, and cost data
- **JSON Format**: Returns a JSON object with comprehensive analytics data

**Example CSV Response Headers**:

```
Content-Type: text/csv
Content-Disposition: attachment; filename=sms_usage_report_123_30d.csv
```

**Example JSON Response**:

```json
{
  "user_id": 123,
  "time_range": "30d",
  "generated_at": "2024-01-15T10:30:00Z",
  "usage_summary": {
    "total_messages": 150,
    "inbound_messages": 75,
    "outbound_messages": 75,
    "success_rate": 98.5,
    "average_processing_time_ms": 250
  },
  "performance_metrics": {
    "successful_messages": 148,
    "failed_messages": 2,
    "success_rate": 98.5,
    "processing_time_metrics": {
      "average_ms": 250,
      "minimum_ms": 120,
      "maximum_ms": 800,
      "p95_ms": 450
    }
  },
  "cost_breakdown": {
    "total_cost_usd": 12.5,
    "inbound_cost_usd": 6.25,
    "outbound_cost_usd": 5.75,
    "mms_cost_usd": 0.5,
    "monthly_number_cost_usd": 1.0,
    "total_with_monthly_fees": 13.5,
    "cost_per_message": 0.083
  }
}
```

**Required Permissions**: `user:read_sms_analytics`

## Admin Analytics Endpoints

### Get System SMS Analytics

Get system-wide SMS analytics and performance metrics.

**Endpoint**: `GET /admin/sms-analytics/system`

**Query Parameters**:

- `time_range` (string, optional): Time range for analytics. Options: `7d`, `30d`, `90d`, `1y`. Default: `30d`

**Response**:

```json
{
  "time_range": "30d",
  "system_performance": {
    "total_messages": 15000,
    "success_rate": 99.2,
    "average_processing_time_ms": 180,
    "active_users": 45,
    "peak_concurrent_users": 12
  },
  "system_costs": {
    "total_cost_usd": 1250.0,
    "cost_per_message": 0.083,
    "top_cost_users": [
      {
        "user_id": 123,
        "cost_usd": 45.5,
        "message_count": 550
      }
    ],
    "cost_distribution": {
      "inbound": 0.6,
      "outbound": 0.35,
      "mms": 0.05
    }
  },
  "performance_trends": {
    "daily_metrics": [
      {
        "date": "2024-01-01",
        "messages": 500,
        "success_rate": 99.1,
        "avg_processing_time": 175
      }
    ],
    "growth_rate": 0.15,
    "peak_usage_hours": [9, 10, 11, 14, 15, 16]
  },
  "generated_at": "2024-01-15T10:30:00Z"
}
```

**Required Permissions**: `system:view_sms_analytics`

### Get Users SMS Analytics

Get SMS analytics for multiple users with pagination.

**Endpoint**: `GET /admin/sms-analytics/users`

**Query Parameters**:

- `time_range` (string, optional): Time range for analytics. Options: `7d`, `30d`, `90d`, `1y`. Default: `30d`
- `limit` (integer, optional): Number of users to return. Range: 1-1000. Default: 100
- `offset` (integer, optional): Number of users to skip. Range: 0+. Default: 0

**Response**:

```json
{
  "time_range": "30d",
  "total_users": 45,
  "limit": 100,
  "offset": 0,
  "user_analytics": [
    {
      "user_id": 123,
      "usage_summary": {
        "total_messages": 550,
        "inbound_messages": 275,
        "outbound_messages": 275,
        "success_rate": 98.9,
        "average_processing_time_ms": 220
      },
      "cost_breakdown": {
        "total_cost_usd": 45.5,
        "cost_per_message": 0.083
      }
    }
  ],
  "generated_at": "2024-01-15T10:30:00Z"
}
```

**Required Permissions**: `system:view_sms_analytics`

### Get SMS Performance Metrics

Get real-time SMS performance monitoring metrics and system health.

**Endpoint**: `GET /admin/sms-performance`

**Response**:

```json
{
  "real_time_metrics": {
    "current_active_users": 8,
    "messages_per_minute": 12,
    "average_response_time_ms": 180,
    "success_rate_last_hour": 99.1,
    "queue_depth": 3,
    "system_load": 0.45
  },
  "sla_compliance": {
    "uptime_percentage": 99.95,
    "response_time_sla": {
      "target_ms": 500,
      "actual_p95_ms": 420,
      "compliance_rate": 98.5
    },
    "delivery_sla": {
      "target_rate": 99.0,
      "actual_rate": 99.2,
      "compliance_rate": 100.0
    }
  },
  "performance_alerts": [
    {
      "severity": "warning",
      "type": "high_response_time",
      "message": "Average response time exceeded 400ms for the last 15 minutes",
      "timestamp": "2024-01-15T10:15:00Z",
      "threshold": 400,
      "actual_value": 420
    }
  ],
  "system_health": {
    "database_status": "healthy",
    "redis_status": "healthy",
    "twilio_status": "healthy",
    "overall_health_score": 95
  },
  "recommendations": [
    {
      "category": "performance",
      "priority": "medium",
      "recommendation": "Consider scaling Redis cache to improve response times",
      "impact": "Could reduce average response time by 15-20%"
    },
    {
      "category": "cost",
      "priority": "low",
      "recommendation": "Implement message batching for high-volume users",
      "impact": "Potential 5-10% cost reduction"
    }
  ],
  "generated_at": "2024-01-15T10:30:00Z"
}
```

**Required Permissions**: `system:view_sms_performance`

### Get Historical Performance

Get historical SMS performance data for trend analysis.

**Endpoint**: `GET /admin/sms-performance/historical`

**Query Parameters**:

- `time_range` (string, optional): Time range for historical data. Options: `7d`, `30d`, `90d`, `1y`. Default: `30d`

**Response**:

```json
{
  "time_range": "30d",
  "historical_performance": {
    "daily_metrics": [
      {
        "date": "2024-01-01",
        "total_messages": 500,
        "success_rate": 99.1,
        "avg_response_time_ms": 175,
        "active_users": 45,
        "cost_usd": 41.5
      }
    ],
    "hourly_patterns": {
      "peak_hours": [9, 10, 11, 14, 15, 16],
      "off_peak_hours": [0, 1, 2, 3, 4, 5],
      "average_messages_per_hour": 20.8
    },
    "trend_analysis": {
      "message_growth_rate": 0.15,
      "performance_trend": "stable",
      "cost_trend": "increasing",
      "user_growth_rate": 0.08
    }
  },
  "generated_at": "2024-01-15T10:30:00Z"
}
```

**Required Permissions**: `system:view_sms_performance`

### Get Performance Alerts

Get current performance alerts and notifications.

**Endpoint**: `GET /admin/sms-performance/alerts`

**Response**:

```json
{
  "alerts": [
    {
      "id": "alert_001",
      "severity": "warning",
      "type": "high_response_time",
      "title": "Response Time Exceeded Threshold",
      "message": "Average response time exceeded 400ms for the last 15 minutes",
      "timestamp": "2024-01-15T10:15:00Z",
      "threshold": 400,
      "actual_value": 420,
      "duration_minutes": 15,
      "status": "active",
      "acknowledged": false
    },
    {
      "id": "alert_002",
      "severity": "info",
      "type": "high_usage",
      "title": "Unusual Usage Pattern Detected",
      "message": "User 123 has sent 200 messages in the last hour (3x normal rate)",
      "timestamp": "2024-01-15T09:45:00Z",
      "threshold": 100,
      "actual_value": 200,
      "duration_minutes": 60,
      "status": "resolved",
      "acknowledged": true
    }
  ],
  "generated_at": "2024-01-15T10:30:00Z"
}
```

**Required Permissions**: `system:view_sms_performance`

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request

```json
{
  "detail": "Invalid time_range. Must be one of: 7d, 30d, 90d, 1y"
}
```

### 401 Unauthorized

```json
{
  "detail": "Authentication required"
}
```

### 403 Forbidden

```json
{
  "detail": "Insufficient permissions. Required: user:read_sms_analytics"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Failed to get SMS analytics"
}
```

## Usage Examples

### Get User Analytics for Last 7 Days

```bash
curl -X GET "https://api.personalassistant.com/api/v1/analytics/me/sms-analytics?time_range=7d" \
  -H "Authorization: Bearer <jwt_token>"
```

### Download CSV Report

```bash
curl -X GET "https://api.personalassistant.com/api/v1/analytics/me/sms-usage-report?format=csv&time_range=30d" \
  -H "Authorization: Bearer <jwt_token>" \
  -o sms_report.csv
```

### Get System Performance Metrics

```bash
curl -X GET "https://api.personalassistant.com/api/v1/analytics/admin/sms-performance" \
  -H "Authorization: Bearer <jwt_token>"
```

## Data Retention

- **User analytics**: Retained for 2 years
- **System analytics**: Retained for 5 years
- **Performance metrics**: Real-time data retained for 30 days, aggregated data for 1 year
- **Cost data**: Retained for 7 years (compliance requirement)

## Rate Limits and Quotas

- **Analytics queries**: Maximum 1000 requests per user per day
- **Report generation**: Maximum 10 reports per user per day
- **Admin queries**: Maximum 5000 requests per admin per day
- **Data export**: Maximum 1GB per export request
