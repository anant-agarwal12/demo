import { useState, useEffect } from 'react'
import { api } from '../api/api'
import AlertCard from '../components/AlertCard'

export default function AlertsPage() {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    status: '',
    acknowledged: ''
  })
  const [selectedAlerts, setSelectedAlerts] = useState([])

  useEffect(() => {
    loadAlerts()
  }, [filters])

  const loadAlerts = async () => {
    setLoading(true)
    try {
      const params = {
        limit: 100
      }
      
      if (filters.status) {
        params.status = filters.status
      }
      
      if (filters.acknowledged !== '') {
        params.acknowledged = filters.acknowledged === 'true'
      }

      const data = await api.getAlerts(params)
      setAlerts(data.alerts || [])
    } catch (err) {
      console.error('Error loading alerts:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleAcknowledge = (alertId) => {
    setAlerts(prev =>
      prev.map(a => a.id === alertId ? { ...a, acknowledged: true } : a)
    )
  }

  const handleSelectAlert = (alertId) => {
    setSelectedAlerts(prev =>
      prev.includes(alertId)
        ? prev.filter(id => id !== alertId)
        : [...prev, alertId]
    )
  }

  const handleSelectAll = () => {
    if (selectedAlerts.length === alerts.length) {
      setSelectedAlerts([])
    } else {
      setSelectedAlerts(alerts.map(a => a.id))
    }
  }

  const handleBulkAcknowledge = async () => {
    for (const alertId of selectedAlerts) {
      try {
        await api.acknowledgeAlert(alertId)
        handleAcknowledge(alertId)
      } catch (err) {
        console.error('Error acknowledging alert:', err)
      }
    }
    setSelectedAlerts([])
  }

  const handleExportCSV = () => {
    const selectedAlertData = alerts.filter(a => selectedAlerts.includes(a.id))
    const csv = [
      ['ID', 'Timestamp', 'Status', 'Identity', 'Confidence', 'Distance', 'Angle', 'Acknowledged'].join(','),
      ...selectedAlertData.map(a => [
        a.id,
        new Date(a.timestamp * 1000).toISOString(),
        a.status,
        a.identity || '',
        a.confidence || '',
        a.distance || '',
        a.angle || '',
        a.acknowledged ? 'Yes' : 'No'
      ].join(','))
    ].join('\n')

    const blob = new Blob([csv], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `doggobot_alerts_${Date.now()}.csv`
    a.click()
    window.URL.revokeObjectURL(url)
  }

  const stats = {
    total: alerts.length,
    friendly: alerts.filter(a => a.status === 'friendly').length,
    unknown: alerts.filter(a => a.status === 'unknown').length,
    suspicious: alerts.filter(a => a.status === 'suspicious').length,
    acknowledged: alerts.filter(a => a.acknowledged).length
  }

  return (
    <div className="container mx-auto px-4 py-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Alert History</h1>
        <p className="text-gray-600">View and manage all detection alerts</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
        <div className="card">
          <p className="text-sm text-gray-600">Total</p>
          <p className="text-2xl font-bold">{stats.total}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-600">Friendly</p>
          <p className="text-2xl font-bold text-green-600">{stats.friendly}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-600">Unknown</p>
          <p className="text-2xl font-bold text-red-600">{stats.unknown}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-600">Suspicious</p>
          <p className="text-2xl font-bold text-orange-600">{stats.suspicious}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-600">Acknowledged</p>
          <p className="text-2xl font-bold">{stats.acknowledged}</p>
        </div>
      </div>

      {/* Filters & Actions */}
      <div className="card mb-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex flex-wrap gap-4">
            <select
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              className="input"
            >
              <option value="">All Statuses</option>
              <option value="friendly">Friendly</option>
              <option value="unknown">Unknown</option>
              <option value="suspicious">Suspicious</option>
            </select>

            <select
              value={filters.acknowledged}
              onChange={(e) => setFilters({ ...filters, acknowledged: e.target.value })}
              className="input"
            >
              <option value="">All Alerts</option>
              <option value="false">Unacknowledged</option>
              <option value="true">Acknowledged</option>
            </select>

            <button
              onClick={loadAlerts}
              disabled={loading}
              className="btn-secondary"
            >
              {loading ? 'Loading...' : 'Refresh'}
            </button>
          </div>

          {selectedAlerts.length > 0 && (
            <div className="flex gap-2">
              <button
                onClick={handleBulkAcknowledge}
                className="btn-primary"
              >
                Acknowledge ({selectedAlerts.length})
              </button>
              <button
                onClick={handleExportCSV}
                className="btn-secondary"
              >
                Export CSV
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Alerts List */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={selectedAlerts.length === alerts.length && alerts.length > 0}
              onChange={handleSelectAll}
              className="w-4 h-4"
            />
            <span className="text-sm font-semibold">Select All</span>
          </label>
          <p className="text-sm text-gray-600">
            Showing {alerts.length} alerts
          </p>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <p className="text-gray-600">Loading alerts...</p>
          </div>
        ) : alerts.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-400">No alerts found</p>
          </div>
        ) : (
          <div className="space-y-4">
            {alerts.map(alert => (
              <div key={alert.id} className="flex items-start space-x-3">
                <input
                  type="checkbox"
                  checked={selectedAlerts.includes(alert.id)}
                  onChange={() => handleSelectAlert(alert.id)}
                  className="mt-6 w-4 h-4"
                />
                <div className="flex-1">
                  <AlertCard
                    alert={alert}
                    onAcknowledge={handleAcknowledge}
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
