import { useState, useEffect } from 'react'
import { useSSE } from '../hooks/useSSE'
import { api } from '../api/api'
import VideoFeed from '../components/VideoFeed'
import AlertCard from '../components/AlertCard'
import OperatorControls from '../components/OperatorControls'
import NLPChat from '../components/NLPChat'

export default function CommandCenter() {
  const { events, isConnected } = useSSE()
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [playSound, setPlaySound] = useState(true)

  // Load initial alerts
  useEffect(() => {
    loadAlerts()
  }, [])

  // Listen for new alerts from SSE
  useEffect(() => {
    const alertEvents = events.filter(e => e.type === 'alert')
    if (alertEvents.length > 0) {
      const newAlert = alertEvents[0].alert
      
      // Add to alerts list if not already present
      setAlerts(prev => {
        const exists = prev.some(a => a.id === newAlert.id)
        if (!exists) {
          // Play notification sound for new alert
          if (playSound) {
            playNotificationSound()
          }
          return [newAlert, ...prev]
        }
        return prev
      })
    }
  }, [events, playSound])

  // Listen for acknowledgements
  useEffect(() => {
    const ackEvents = events.filter(e => e.type === 'ack')
    if (ackEvents.length > 0) {
      const alertId = ackEvents[0].alert_id
      setAlerts(prev => 
        prev.map(a => a.id === alertId ? { ...a, acknowledged: true } : a)
      )
    }
  }, [events])

  const loadAlerts = async () => {
    setLoading(true)
    try {
      const data = await api.getAlerts({ limit: 50 })
      setAlerts(data.alerts || [])
    } catch (err) {
      console.error('Error loading alerts:', err)
    } finally {
      setLoading(false)
    }
  }

  const playNotificationSound = () => {
    // Simple notification beep (you could replace with actual audio file)
    const audioContext = new (window.AudioContext || window.webkitAudioContext)()
    const oscillator = audioContext.createOscillator()
    const gainNode = audioContext.createGain()
    
    oscillator.connect(gainNode)
    gainNode.connect(audioContext.destination)
    
    oscillator.frequency.value = 800
    oscillator.type = 'sine'
    
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime)
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5)
    
    oscillator.start(audioContext.currentTime)
    oscillator.stop(audioContext.currentTime + 0.5)
  }

  const handleAcknowledge = (alertId) => {
    setAlerts(prev =>
      prev.map(a => a.id === alertId ? { ...a, acknowledged: true } : a)
    )
  }

  const unacknowledgedAlerts = alerts.filter(a => !a.acknowledged)
  const recentAlerts = alerts.slice(0, 10)

  return (
    <div className="container mx-auto px-4 py-6">
      {/* Header Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Connection</p>
              <p className="text-2xl font-bold">{isConnected ? '? Online' : '? Offline'}</p>
            </div>
            <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
          </div>
        </div>
        
        <div className="card">
          <p className="text-sm text-gray-600">Total Alerts</p>
          <p className="text-2xl font-bold">{alerts.length}</p>
        </div>
        
        <div className="card">
          <p className="text-sm text-gray-600">Unacknowledged</p>
          <p className="text-2xl font-bold text-red-600">{unacknowledgedAlerts.length}</p>
        </div>
        
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Sound</p>
              <p className="text-sm font-semibold">{playSound ? 'Enabled' : 'Muted'}</p>
            </div>
            <button
              onClick={() => setPlaySound(!playSound)}
              className="btn-secondary text-xs px-2 py-1"
            >
              {playSound ? '??' : '??'}
            </button>
          </div>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Video & Controls */}
        <div className="lg:col-span-2 space-y-6">
          <VideoFeed />
          <OperatorControls />
          <NLPChat sseEvents={events} />
        </div>

        {/* Right Column - Alerts */}
        <div className="space-y-4">
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">Live Alerts</h2>
              <button
                onClick={loadAlerts}
                disabled={loading}
                className="btn-secondary text-sm px-3 py-1"
              >
                {loading ? '...' : '? Refresh'}
              </button>
            </div>

            <div className="space-y-4 max-h-screen overflow-y-auto">
              {recentAlerts.length === 0 && (
                <p className="text-gray-400 text-center py-8">No alerts yet</p>
              )}
              {recentAlerts.map(alert => (
                <AlertCard
                  key={alert.id}
                  alert={alert}
                  onAcknowledge={handleAcknowledge}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
