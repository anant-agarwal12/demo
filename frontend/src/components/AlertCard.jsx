import { useState } from 'react'
import { api } from '../api/api'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export default function AlertCard({ alert, onAcknowledge }) {
  const [expanded, setExpanded] = useState(false)
  const [acknowledging, setAcknowledging] = useState(false)

  const statusColors = {
    friendly: 'bg-green-500',
    unknown: 'bg-red-500',
    suspicious: 'bg-orange-500'
  }

  const statusLabels = {
    friendly: 'FRIENDLY',
    unknown: 'UNKNOWN',
    suspicious: 'SUSPICIOUS'
  }

  const handleAcknowledge = async () => {
    setAcknowledging(true)
    try {
      await api.acknowledgeAlert(alert.id)
      if (onAcknowledge) {
        onAcknowledge(alert.id)
      }
    } catch (err) {
      console.error('Error acknowledging alert:', err)
    } finally {
      setAcknowledging(false)
    }
  }

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp * 1000)
    return date.toLocaleString()
  }

  return (
    <div className={`card ${alert.acknowledged ? 'opacity-60' : ''}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <span className={`px-2 py-1 text-xs font-bold text-white rounded ${statusColors[alert.status] || 'bg-gray-500'}`}>
              {statusLabels[alert.status] || 'UNKNOWN'}
            </span>
            {alert.identity && (
              <span className="text-sm font-semibold">{alert.identity}</span>
            )}
            {alert.confidence && (
              <span className="text-xs text-gray-500">
                {(alert.confidence * 100).toFixed(0)}% confidence
              </span>
            )}
          </div>

          <div className="text-sm text-gray-600 space-y-1">
            <p>{formatTimestamp(alert.timestamp)}</p>
            {alert.distance && (
              <p>Distance: {alert.distance.toFixed(2)}m | Angle: {(alert.angle * 180 / Math.PI).toFixed(1)}?</p>
            )}
          </div>

          {alert.snapshot_path && (
            <div className="mt-3">
              <img
                src={`${API_BASE}/${alert.snapshot_path}`}
                alt="Detection snapshot"
                className={`rounded-lg cursor-pointer ${expanded ? 'max-w-full' : 'max-w-xs'}`}
                onClick={() => setExpanded(!expanded)}
              />
            </div>
          )}
        </div>

        <div className="flex flex-col space-y-2 ml-4">
          {!alert.acknowledged && (
            <button
              onClick={handleAcknowledge}
              disabled={acknowledging}
              className="btn-primary text-sm px-3 py-1"
            >
              {acknowledging ? 'Ack...' : 'Ack'}
            </button>
          )}
          {alert.snapshot_path && (
            <a
              href={`${API_BASE}/${alert.snapshot_path}`}
              download
              className="btn-secondary text-sm px-3 py-1 text-center"
            >
              Download
            </a>
          )}
        </div>
      </div>
    </div>
  )
}
