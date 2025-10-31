import { useEffect, useRef, useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export function useSSE() {
  const [events, setEvents] = useState([])
  const [isConnected, setIsConnected] = useState(false)
  const eventSourceRef = useRef(null)
  const reconnectTimeoutRef = useRef(null)

  const connect = () => {
    try {
      const eventSource = new EventSource(`${API_BASE}/stream`)
      eventSourceRef.current = eventSource

      eventSource.onopen = () => {
        console.log('SSE connected')
        setIsConnected(true)
      }

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          
          // Ignore heartbeat events for the events array
          if (data.type !== 'heartbeat') {
            setEvents((prev) => [data, ...prev].slice(0, 100)) // Keep last 100 events
          }
        } catch (err) {
          console.error('Error parsing SSE data:', err)
        }
      }

      eventSource.onerror = (error) => {
        console.error('SSE error:', error)
        setIsConnected(false)
        eventSource.close()
        
        // Reconnect after 5 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('Reconnecting SSE...')
          connect()
        }, 5000)
      }
    } catch (err) {
      console.error('Error creating SSE connection:', err)
      setIsConnected(false)
    }
  }

  useEffect(() => {
    connect()

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
    }
  }, [])

  return { events, isConnected }
}
