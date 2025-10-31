import { useState, useRef, useEffect } from 'react'
import { api } from '../api/api'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export default function NLPChat({ sseEvents }) {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([])
  const [sending, setSending] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Listen for NLP events from SSE
  useEffect(() => {
    const nlpEvents = sseEvents.filter(e => e.type === 'nlp')
    if (nlpEvents.length > 0) {
      const latestEvent = nlpEvents[0]
      const existing = messages.find(m => m.timestamp === latestEvent.timestamp)
      if (!existing) {
        setMessages(prev => [...prev, {
          type: 'response',
          text: latestEvent.text,
          tts: latestEvent.tts,
          timestamp: Date.now()
        }])
      }
    }
  }, [sseEvents])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || sending) return

    const userMessage = input.trim()
    setInput('')
    
    // Add user message
    setMessages(prev => [...prev, {
      type: 'user',
      text: userMessage,
      timestamp: Date.now()
    }])

    setSending(true)
    try {
      const response = await api.sendNLPCommand(userMessage)
      
      // Add response message
      setMessages(prev => [...prev, {
        type: 'response',
        text: response.text,
        tts: response.tts,
        timestamp: Date.now()
      }])

      // Play TTS if available
      if (response.tts) {
        const audio = new Audio(`${API_BASE}/${response.tts}`)
        audio.play().catch(err => console.error('Error playing audio:', err))
      }
    } catch (err) {
      console.error('Error sending NLP command:', err)
      setMessages(prev => [...prev, {
        type: 'error',
        text: 'Error: Could not send command',
        timestamp: Date.now()
      }])
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="card flex flex-col h-96">
      <h2 className="text-xl font-bold mb-4">NLP Command Chat</h2>
      
      <div className="flex-1 overflow-y-auto space-y-3 mb-4">
        {messages.length === 0 && (
          <p className="text-gray-400 text-sm">Type a command like "status", "stop", or "investigate"</p>
        )}
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs px-4 py-2 rounded-lg ${
                msg.type === 'user'
                  ? 'bg-blue-600 text-white'
                  : msg.type === 'error'
                  ? 'bg-red-100 text-red-800'
                  : 'bg-gray-200 text-gray-800'
              }`}
            >
              {msg.text}
              {msg.tts && (
                <button
                  onClick={() => {
                    const audio = new Audio(`${API_BASE}/${msg.tts}`)
                    audio.play()
                  }}
                  className="ml-2 text-xs underline"
                >
                  ?? Play
                </button>
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="flex space-x-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a command..."
          className="flex-1 input"
          disabled={sending}
        />
        <button
          type="submit"
          disabled={sending || !input.trim()}
          className="btn-primary"
        >
          {sending ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  )
}
