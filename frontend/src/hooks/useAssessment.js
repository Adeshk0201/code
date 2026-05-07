import { useRef, useState, useCallback } from 'react'

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/assessment'

export function useAssessment() {
  const ws = useRef(null)
  const [connected, setConnected] = useState(false)
  const [message, setMessage] = useState(null)
  const [error, setError] = useState(null)

  const connect = useCallback((onMessage) => {
    ws.current = new WebSocket(WS_URL)

    ws.current.onopen = () => setConnected(true)

    ws.current.onmessage = (e) => {
      const data = JSON.parse(e.data)
      setMessage(data)
      if (onMessage) onMessage(data)
    }

    ws.current.onerror = () => setError('WebSocket connection failed.')
    ws.current.onclose = () => setConnected(false)
  }, [])

  const send = useCallback((type, payload) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ type, payload }))
    }
  }, [])

  const disconnect = useCallback(() => {
    ws.current?.close()
  }, [])

  return { connected, message, error, connect, send, disconnect }
}