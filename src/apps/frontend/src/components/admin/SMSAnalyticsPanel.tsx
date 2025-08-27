import React, { useState, useEffect, useCallback } from 'react';
import { useAuthStore } from '@/stores/authStore';
import { RefreshCw, AlertTriangle, TrendingUp, Activity, DollarSign, Clock } from 'lucide-react';

interface SystemAnalyticsData {
  system_performance: {
    total_messages: number;
    successful_messages: number;
    failed_messages: number;
    success_rate: number;
    average_processing_time_ms: number;
    unique_active_users: number;
    hourly_activity_patterns: {
      peak_hour: number | null;
      low_activity_hour: number | null;
      total_activity: number;
    };
  };
  system_costs: {
    total_cost_usd: number;
    inbound_cost_usd: number;
    outbound_cost_usd: number;
    mms_cost_usd: number;
    international_cost_usd: number;
    total_messages: number;
    unique_users: number;
    average_cost_per_user: number;
    top_cost_users: Array<{
      user_id: number;
      cost_usd: number;
    }>;
  };
  performance_trends: {
    daily_performance: Array<{
      date: string;
      total_messages: number;
      success_rate: number;
      average_processing_time_ms: number;
    }>;
    trend_analysis: {
      success_rate_trend: {
        trend: string;
        change_percentage: number;
      };
      processing_time_trend: {
        trend: string;
        change_percentage: number;
      };
    };
  };
}

interface PerformanceMetricsData {
  real_time_metrics: {
    total_messages: number;
    successful_messages: number;
    failed_messages: number;
    success_rate_percent: number;
    average_response_time_ms: number;
    active_users: number;
    peak_users: number;
  };
  sla_compliance: {
    sla_status: string;
    compliance_percentage: number;
    overall_health: string;
    sla_checks: Record<string, any>;
  };
  performance_alerts: Array<{
    id: string;
    type: string;
    severity: string;
    metric: string;
    message: string;
    timestamp: string;
    actionable: boolean;
    recommendation: string;
  }>;
  system_health: {
    system_status: string;
    health_score: number;
    active_alerts: number;
    critical_alerts: number;
    warning_alerts: number;
  };
  recommendations: Array<{
    category: string;
    priority: string;
    title: string;
    description: string;
    actions: string[];
    estimated_impact: string;
    effort_required: string;
  }>;
}

interface SMSAnalyticsPanelProps {
  timeRange?: '7d' | '30d' | '90d' | '1y';
}

const SMSAnalyticsPanel: React.FC<SMSAnalyticsPanelProps> = ({
  timeRange = '30d',
}) => {
  const { user } = useAuthStore();
  const [systemAnalytics, setSystemAnalytics] = useState<SystemAnalyticsData | null>(null);
  const [performanceMetrics, setPerformanceMetrics] = useState<PerformanceMetricsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTimeRange, setSelectedTimeRange] = useState(timeRange);
  const [activeTab, setActiveTab] = useState<'overview' | 'performance' | 'costs' | 'alerts'>('overview');
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      fetchSystemAnalytics();
      fetchPerformanceMetrics();
    }, 30000); // 30 seconds

    return () => clearInterval(interval);
  }, [autoRefresh, selectedTimeRange]);

  // Initial data fetch
  useEffect(() => {
    fetchSystemAnalytics();
    fetchPerformanceMetrics();
  }, [selectedTimeRange]);

  const fetchSystemAnalytics = useCallback(async () => {
    try {
      const response = await fetch(
        `/api/v1/analytics/admin/sms-analytics/system?time_range=${selectedTimeRange}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch system analytics');
      }

      const data = await response.json();
      setSystemAnalytics(data);
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Error fetching system analytics:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch system analytics');
    }
  }, [selectedTimeRange]);

  const fetchPerformanceMetrics = useCallback(async () => {
    try {
      const response = await fetch(
        `/api/v1/analytics/admin/sms-performance`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch performance metrics');
      }

      const data = await response.json();
      setPerformanceMetrics(data);
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Error fetching performance metrics:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch performance metrics');
    } finally {
      setLoading(false);
    }
  }, []);

  const handleManualRefresh = () => {
    setIsRefreshing(true);
    Promise.all([fetchSystemAnalytics(), fetchPerformanceMetrics()]).finally(() => {
      setIsRefreshing(false);
    });
  };

  const toggleAutoRefresh = () => {
    setAutoRefresh(!autoRefresh);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const formatTimeRange = (range: string) => {
    const rangeMap: Record<string, string> = {
      '7d': '7 Days',
      '30d': '30 Days',
      '90d': '90 Days',
      '1y': '1 Year',
    };
    return rangeMap[range] || range;
  };

  const getHealthStatusColor = (status: string) => {
    const statusColors: Record<string, string> = {
      healthy: 'text-green-600',
      degraded: 'text-yellow-600',
      unhealthy: 'text-orange-600',
      critical: 'text-red-600',
    };
    return statusColors[status] || 'text-gray-600';
  };

  const getSeverityColor = (severity: string) => {
    const severityColors: Record<string, string> = {
      critical: 'bg-red-100 text-red-800',
      warning: 'bg-yellow-100 text-yellow-800',
      normal: 'bg-green-100 text-green-800',
    };
    return severityColors[severity] || 'bg-gray-100 text-gray-800';
  };

  if (loading && !systemAnalytics) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-1/3"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="h-20 bg-gray-200 rounded"></div>
            <div className="h-20 bg-gray-200 rounded"></div>
            <div className="h-20 bg-gray-200 rounded"></div>
            <div className="h-20 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="text-center py-8">
          <div className="text-red-500 mb-4">
            <AlertTriangle className="w-16 h-16 mx-auto" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Error Loading Analytics</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={handleManualRefresh}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      {/* Header with Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 space-y-3 sm:space-y-0">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">System Analytics Dashboard</h3>
          <p className="text-sm text-gray-600">
            {formatTimeRange(selectedTimeRange)} • 
            {lastUpdated && (
              <span className="ml-2">
                Last updated: {lastUpdated.toLocaleTimeString()}
              </span>
            )}
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          {/* Auto-refresh toggle */}
          <button
            onClick={toggleAutoRefresh}
            className={`px-3 py-1.5 text-xs rounded-lg transition-colors ${
              autoRefresh 
                ? 'bg-green-100 text-green-700 hover:bg-green-200' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {autoRefresh ? 'Auto-refresh ON' : 'Auto-refresh OFF'}
          </button>
          
          {/* Manual refresh */}
          <button
            onClick={handleManualRefresh}
            disabled={isRefreshing}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
            title="Refresh data"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          </button>
          
          {/* Time range selector */}
          <select
            value={selectedTimeRange}
            onChange={(e) => setSelectedTimeRange(e.target.value as '7d' | '30d' | '90d' | '1y')}
            className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
          </select>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', label: 'Overview' },
            { id: 'performance', label: 'Performance' },
            { id: 'costs', label: 'Costs' },
            { id: 'alerts', label: 'Alerts' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && systemAnalytics && (
        <div className="space-y-6">
          {/* System Performance Overview */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {systemAnalytics.system_performance.total_messages.toLocaleString()}
              </div>
              <div className="text-sm text-blue-800">Total Messages</div>
            </div>
            
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {systemAnalytics.system_performance.success_rate}%
              </div>
              <div className="text-sm text-green-800">Success Rate</div>
            </div>
            
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">
                {systemAnalytics.system_performance.unique_active_users}
              </div>
              <div className="text-sm text-purple-800">Active Users</div>
            </div>
            
            <div className="bg-orange-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">
                {formatCurrency(systemAnalytics.system_costs.total_cost_usd)}
              </div>
              <div className="text-sm text-orange-800">Total Cost</div>
            </div>
          </div>

          {/* Performance Trends */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-semibold text-gray-900 mb-3">Performance Trends</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Success Rate</h4>
                <div className="text-lg font-bold text-gray-900">
                  {systemAnalytics.performance_trends.trend_analysis.success_rate_trend.trend}
                </div>
                <div className="text-sm text-gray-600">
                  {systemAnalytics.performance_trends.trend_analysis.success_rate_trend.change_percentage > 0 ? '+' : ''}
                  {systemAnalytics.performance_trends.trend_analysis.success_rate_trend.change_percentage}% change
                </div>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Response Time</h4>
                <div className="text-lg font-bold text-gray-900">
                  {systemAnalytics.performance_trends.trend_analysis.processing_time_trend.trend}
                </div>
                <div className="text-sm text-gray-600">
                  {systemAnalytics.performance_trends.trend_analysis.processing_time_trend.change_percentage > 0 ? '+' : ''}
                  {systemAnalytics.performance_trends.trend_analysis.processing_time_trend.change_percentage}% change
                </div>
              </div>
            </div>
          </div>

          {/* Top Cost Users */}
          {systemAnalytics.system_costs.top_cost_users.length > 0 && (
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold text-gray-900 mb-3">Top Cost Users</h3>
              <div className="space-y-2">
                {systemAnalytics.system_costs.top_cost_users.slice(0, 5).map((user, index) => (
                  <div key={user.user_id} className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">User {user.user_id}</span>
                    <span className="font-medium">{formatCurrency(user.cost_usd)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Performance Tab */}
      {activeTab === 'performance' && performanceMetrics && (
        <div className="space-y-6">
          {/* Real-time Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {performanceMetrics.real_time_metrics.total_messages}
              </div>
              <div className="text-sm text-blue-800">Messages (1h)</div>
            </div>
            
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {performanceMetrics.real_time_metrics.success_rate_percent}%
              </div>
              <div className="text-sm text-green-800">Success Rate</div>
            </div>
            
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">
                {performanceMetrics.real_time_metrics.average_response_time_ms}ms
              </div>
              <div className="text-sm text-purple-800">Avg Response</div>
            </div>
            
            <div className="bg-orange-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">
                {performanceMetrics.real_time_metrics.active_users}
              </div>
              <div className="text-sm text-orange-800">Active Users</div>
            </div>
          </div>

          {/* SLA Compliance */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-semibold text-gray-900 mb-3">SLA Compliance</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <div className={`text-lg font-bold ${getHealthStatusColor(performanceMetrics.sla_compliance.overall_health)}`}>
                  {performanceMetrics.sla_compliance.overall_health.toUpperCase()}
                </div>
                <div className="text-sm text-gray-600">Overall Health</div>
              </div>
              
              <div>
                <div className="text-lg font-bold text-gray-900">
                  {performanceMetrics.sla_compliance.compliance_percentage}%
                </div>
                <div className="text-sm text-gray-600">Compliance</div>
              </div>
              
              <div>
                <div className="text-lg font-bold text-gray-900">
                  {performanceMetrics.system_health.health_score}
                </div>
                <div className="text-sm text-gray-600">Health Score</div>
              </div>
            </div>
          </div>

          {/* Performance Recommendations */}
          {performanceMetrics.recommendations.length > 0 && (
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold text-gray-900 mb-3">Performance Recommendations</h3>
              <div className="space-y-3">
                {performanceMetrics.recommendations.slice(0, 3).map((rec, index) => (
                  <div key={index} className="border-l-4 border-blue-500 pl-3">
                    <h4 className="font-medium text-gray-900">{rec.title}</h4>
                    <p className="text-sm text-gray-600 mb-2">{rec.description}</p>
                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                      <span className={`px-2 py-1 rounded ${getSeverityColor(rec.priority)}`}>
                        {rec.priority}
                      </span>
                      <span>Impact: {rec.estimated_impact}</span>
                      <span>Effort: {rec.effort_required}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Costs Tab */}
      {activeTab === 'costs' && systemAnalytics && (
        <div className="space-y-6">
          {/* Cost Overview */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="bg-red-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-red-600">
                {formatCurrency(systemAnalytics.system_costs.total_cost_usd)}
              </div>
              <div className="text-sm text-red-800">Total Cost</div>
            </div>
            
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {formatCurrency(systemAnalytics.system_costs.average_cost_per_user)}
              </div>
              <div className="text-sm text-blue-800">Avg Cost per User</div>
            </div>
            
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {systemAnalytics.system_costs.unique_users}
              </div>
              <div className="text-sm text-green-800">Active Users</div>
            </div>
          </div>

          {/* Cost Breakdown */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-semibold text-gray-900 mb-3">Cost Breakdown</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Inbound Messages:</span>
                  <span className="font-medium">{formatCurrency(systemAnalytics.system_costs.inbound_cost_usd)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Outbound Messages:</span>
                  <span className="font-medium">{formatCurrency(systemAnalytics.system_costs.outbound_cost_usd)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">MMS Messages:</span>
                  <span className="font-medium">{formatCurrency(systemAnalytics.system_costs.mms_cost_usd)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">International:</span>
                  <span className="font-medium">{formatCurrency(systemAnalytics.system_costs.international_cost_usd)}</span>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Total Messages:</span>
                  <span className="font-medium">{systemAnalytics.system_costs.total_messages.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Cost per Message:</span>
                  <span className="font-medium">{formatCurrency(systemAnalytics.system_costs.total_cost_usd / systemAnalytics.system_costs.total_messages)}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Alerts Tab */}
      {activeTab === 'alerts' && performanceMetrics && (
        <div className="space-y-6">
          {/* Alert Summary */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-red-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-red-600">
                {performanceMetrics.system_health.critical_alerts}
              </div>
              <div className="text-sm text-red-800">Critical Alerts</div>
            </div>
            
            <div className="bg-yellow-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-yellow-600">
                {performanceMetrics.system_health.warning_alerts}
              </div>
              <div className="text-sm text-yellow-800">Warning Alerts</div>
            </div>
            
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {performanceMetrics.system_health.active_alerts}
              </div>
              <div className="text-sm text-blue-800">Total Alerts</div>
            </div>
          </div>

          {/* Active Alerts */}
          {performanceMetrics.performance_alerts.length > 0 ? (
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold text-gray-900 mb-3">Active Alerts</h3>
              <div className="space-y-3">
                {performanceMetrics.performance_alerts.map((alert) => (
                  <div key={alert.id} className="border-l-4 border-red-500 pl-3 bg-white p-3 rounded">
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-medium text-gray-900">{alert.message}</h4>
                      <span className={`px-2 py-1 rounded text-xs ${getSeverityColor(alert.severity)}`}>
                        {alert.severity}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{alert.recommendation}</p>
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>Type: {alert.type}</span>
                      <span>{new Date(alert.timestamp).toLocaleString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="bg-green-50 p-4 rounded-lg text-center">
              <div className="text-green-600 font-medium">No active alerts</div>
              <div className="text-sm text-green-700">System is running smoothly</div>
            </div>
          )}
        </div>
      )}

      {/* Last Updated */}
      <div className="text-xs text-gray-500 text-center mt-6">
        Last updated: {new Date().toLocaleString()}
      </div>
    </div>
  );
};

export default SMSAnalyticsPanel;
