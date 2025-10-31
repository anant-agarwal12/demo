import { useState } from 'react'
import { api } from '../api/api'

export default function OperatorControls({ onCommandSent }) {
  const [loading, setLoading] = useState(null)

  const sendCommand = async (command) => {
    setLoading(command)
    try {
      const response = await api.sendNLPCommand(command)
      if (onCommandSent) {
        onCommandSent(response)
      }
    } catch (err) {
      console.error('Error sending command:', err)
    } finally {
      setLoading(null)
    }
  }

  const buttons = [
    { label: 'Start Patrol', command: 'start patrol', color: 'btn-success' },
    { label: 'Stop', command: 'stop', color: 'btn-danger' },
    { label: 'Status', command: 'status', color: 'btn-secondary' },
    { label: 'Return Home', command: 'return home', color: 'btn-secondary' },
    { label: 'Follow', command: 'follow', color: 'btn-primary' },
    { label: 'Investigate', command: 'investigate', color: 'btn-primary' },
    { label: 'Sound Alarm', command: 'alarm', color: 'btn-danger' },
    { label: 'Greet', command: 'greet', color: 'btn-secondary' }
  ]

  return (
    <div className="card">
      <h2 className="text-xl font-bold mb-4">Operator Controls</h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {buttons.map((btn) => (
          <button
            key={btn.command}
            onClick={() => sendCommand(btn.command)}
            disabled={loading === btn.command}
            className={btn.color}
          >
            {loading === btn.command ? '...' : btn.label}
          </button>
        ))}
      </div>
    </div>
  )
}
