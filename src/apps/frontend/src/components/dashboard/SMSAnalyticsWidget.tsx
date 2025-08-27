import React, { useState, useEffect, useCallback } from 'react';
import { useAuthStore } from '@/stores/authStore';
import { RefreshCw, Download, BarChart3, TrendingUp, DollarSign, Clock } from 'lucide-react';
import { Select } from '@/components/ui';

interface SMSAnalyticsData {
  usage_summary: {
    total_messages: number;
    inbound_messages: number;
    outbound_messages: number;
    success_rate: number;
    average_processing_time_ms: number;
    total_message_length: number;
    usage_patterns: {
      hourly_distribution: Record<string, number>;
      peak_hour: number | null;
      low_activity_hour: number | null;
    };
  };
  usage_trends: {
    daily_usage: Array<{
      date: string;
      message_count: number;
    }>;
    trend_analysis: {
      trend: string;
      change_percentage: number;
    };
  };
  performance_metrics: {
    total_messages: number;
    successful_messages: number;
    failed_messages: number;
    success_rate: number;
    processing_time_metrics: {
      average_ms: number;
      minimum_ms: number;
      maximum_ms: number;
    };
  };
  message_breakdown: {
    inbound_breakdown: {
      total_messages: number;
      success_rate: number;
      average_length: number;
    };
    outbound_breakdown: {
      total_messages: number;
      success_rate: number;
      average_length: number;
    };
  };
}

interface SMSCostData {
  cost_breakdown: {
    current_period_costs: {
      total_cost_usd: number;
      inbound_cost_usd: number;
      outbound_cost_usd: number;
      mms_cost_usd: number;
      cost_per_message: number;
    };
    optimization_tips: string[];
  };
  cost_trends: {
    trend: string;
    change_percentage: number;
  };
}

interface SMSAnalyticsWidgetProps {
  timeRange?: '7d' | '30d' | '90d' | '1y';
  showCosts?: boolean;
  showPerformance?: boolean;
}

const SMSAnalyticsWidget: React.FC<SMSAnalyticsWidgetProps> = ({ 
  timeRange = '30d', 
  showCosts = true, 
  showPerformance = true 
}) => {
  const { user } = useAuthStore();
  const [analyticsData, setAnalyticsData] = useState<SMSAnalyticsData | null>(null);
  const [costData, setCostData] = useState<SMSCostData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTimeRange, setSelectedTimeRange] = useState(timeRange);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      fetchAnalyticsData();
    }, 30000); // 30 seconds

    return () => clearInterval(interval);
  }, [autoRefresh, selectedTimeRange]);

  // Initial data fetch
  useEffect(() => {
    fetchAnalyticsData();
  }, [selectedTimeRange]);

  const fetchAnalyticsData = useCallback(async () => {
    if (isRefreshing) return;
    
    setIsRefreshing(true);
    try {
      setError(null);
      
      // Fetch analytics data
      const analyticsResponse = await fetch(
        `/api/v1/analytics/me/sms-analytics?time_range=${selectedTimeRange}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          },
        }
      );

      if (!analyticsResponse.ok) {
        throw new Error('Failed to fetch analytics data');
      }

      const analytics = await analyticsResponse.json();
      setAnalyticsData(analytics);

      // Fetch cost data if enabled
      if (showCosts) {
        const costResponse = await fetch(
          `/api/v1/analytics/me/sms-costs?time_range=${selectedTimeRange}`,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            },
          }
        );

        if (costResponse.ok) {
          const costs = await costResponse.json();
          setCostData(costs);
        }
      }

      setLastUpdated(new Date());
    } catch (err) {
      console.error('Error fetching analytics data:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch analytics data');
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  }, [selectedTimeRange, showCosts, isRefreshing]);

  const handleManualRefresh = () => {
    fetchAnalyticsData();
  };

  const toggleAutoRefresh = () => {
    setAutoRefresh(!autoRefresh);
  };

  const downloadReport = async (format: 'csv' | 'json') => {
    try {
      const response = await fetch(
        `/api/v1/analytics/me/sms-usage-report?format=${format}&time_range=${selectedTimeRange}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to download report');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `sms_usage_report_${selectedTimeRange}_${new Date().toISOString().split('T')[0]}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Error downloading report:', err);
      setError('Failed to download report');
    }
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

  if (loading && !analyticsData) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-1/3"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
            <BarChart3 className="w-16 h-16 mx-auto" />
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

  if (!analyticsData) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="text-center py-8">
          <div className="text-gray-400 mb-4">
            <BarChart3 className="w-16 h-16 mx-auto" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No Analytics Data</h3>
          <p className="text-gray-600">No SMS usage data available for the selected time period.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      {/* Header with Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 space-y-3 sm:space-y-0">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">SMS Usage Analytics</h3>
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
          <Select
            value={selectedTimeRange}
            onChange={(value) => setSelectedTimeRange(value as '7d' | '30d' | '90d' | '1y')}
            options={[
              { value: '7d', label: 'Last 7 days' },
              { value: '30d', label: 'Last 30 days' },
              { value: '90d', label: 'Last 90 days' },
              { value: '1y', label: 'Last year' }
            ]}
            placeholder="Select time range"
            className="w-48"
          />
          
          {/* Download buttons */}
          <div className="flex space-x-2">
            <button
              onClick={() => downloadReport('csv')}
              className="px-3 py-1.5 text-xs bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors flex items-center space-x-1"
            >
              <Download className="w-3 h-3" />
              <span>CSV</span>
            </button>
            <button
              onClick={() => downloadReport('json')}
              className="px-3 py-1.5 text-xs bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors flex items-center space-x-1"
            >
              <Download className="w-3 h-3" />
              <span>JSON</span>
            </button>
          </div>
        </div>
      </div>

      {/* Usage Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-blue-600">
            {analyticsData.usage_summary.total_messages}
          </div>
          <div className="text-sm text-blue-800">Total Messages</div>
        </div>
        
        <div className="bg-green-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-green-600">
            {analyticsData.usage_summary.success_rate}%
          </div>
          <div className="text-sm text-green-800">Success Rate</div>
        </div>
        
        <div className="bg-purple-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-purple-600">
            {analyticsData.usage_summary.average_processing_time_ms}ms
          </div>
          <div className="text-sm text-purple-800">Avg Response Time</div>
        </div>
        
        <div className="bg-orange-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-orange-600">
            {analyticsData.usage_summary.total_message_length}
          </div>
          <div className="text-sm text-orange-800">Total Characters</div>
        </div>
      </div>

      {/* Message Direction Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="font-semibold text-gray-900 mb-3">Message Direction</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Inbound:</span>
              <span className="font-medium">{analyticsData.usage_summary.inbound_messages}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Outbound:</span>
              <span className="font-medium">{analyticsData.usage_summary.outbound_messages}</span>
            </div>
          </div>
        </div>
        
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="font-semibold text-gray-900 mb-3">Performance</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Successful:</span>
              <span className="font-medium text-green-600">
                {analyticsData.performance_metrics.successful_messages}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Failed:</span>
              <span className="font-medium text-red-600">
                {analyticsData.performance_metrics.failed_messages}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Cost Analysis */}
      {showCosts && costData && (
        <div className="bg-gray-50 p-4 rounded-lg mb-6">
          <h3 className="font-semibold text-gray-900 mb-3">Cost Analysis</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <div className="text-lg font-bold text-gray-900">
                {formatCurrency(costData.cost_breakdown.current_period_costs.total_cost_usd)}
              </div>
              <div className="text-sm text-gray-600">Total Cost</div>
            </div>
            <div>
              <div className="text-lg font-bold text-gray-900">
                {formatCurrency(costData.cost_breakdown.current_period_costs.cost_per_message)}
              </div>
              <div className="text-sm text-gray-600">Cost per Message</div>
            </div>
            <div>
              <div className="text-lg font-bold text-gray-900">
                {costData.cost_trends.trend}
              </div>
              <div className="text-sm text-gray-600">Cost Trend</div>
            </div>
          </div>
          
          {/* Optimization Tips */}
          {costData.cost_breakdown.optimization_tips.length > 0 && (
            <div className="mt-4">
              <h4 className="font-medium text-gray-900 mb-2">Optimization Tips</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                {costData.cost_breakdown.optimization_tips.slice(0, 3).map((tip, index) => (
                  <li key={index} className="flex items-start">
                    <span className="text-blue-500 mr-2">•</span>
                    {tip}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Performance Metrics */}
      {showPerformance && (
        <div className="bg-gray-50 p-4 rounded-lg mb-6">
          <h3 className="font-semibold text-gray-900 mb-3">Performance Metrics</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <div className="text-lg font-bold text-gray-900">
                {analyticsData.performance_metrics.processing_time_metrics.average_ms}ms
              </div>
              <div className="text-sm text-gray-600">Avg Response Time</div>
            </div>
            <div>
              <div className="text-lg font-bold text-gray-900">
                {analyticsData.performance_metrics.processing_time_metrics.minimum_ms}ms
              </div>
              <div className="text-sm text-gray-600">Min Response Time</div>
            </div>
            <div>
              <div className="text-lg font-bold text-gray-900">
                {analyticsData.performance_metrics.processing_time_metrics.maximum_ms}ms
              </div>
              <div className="text-sm text-gray-600">Max Response Time</div>
            </div>
          </div>
        </div>
      )}

      {/* Usage Trends */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h3 className="font-semibold text-gray-900 mb-3">Usage Trends</h3>
        <div className="flex items-center justify-between">
          <div>
            <div className="text-lg font-bold text-gray-900">
              {analyticsData.usage_trends.trend_analysis.trend}
            </div>
            <div className="text-sm text-gray-600">
              {analyticsData.usage_trends.trend_analysis.change_percentage > 0 ? '+' : ''}
              {analyticsData.usage_trends.trend_analysis.change_percentage}% change
            </div>
          </div>
          
          {analyticsData.usage_summary.usage_patterns.peak_hour !== null && (
            <div className="text-right">
              <div className="text-lg font-bold text-gray-900">
                {analyticsData.usage_summary.usage_patterns.peak_hour}:00
              </div>
              <div className="text-sm text-gray-600">Peak Hour</div>
            </div>
          )}
        </div>
      </div>

      {/* Last Updated */}
      <div className="text-xs text-gray-500 text-center mt-4">
        Last updated: {new Date().toLocaleString()}
      </div>
    </div>
  );
};

export default SMSAnalyticsWidget;
