import { api } from '../api/api'
import { useEffect, useRef, useState } from 'react'

export default function VideoFeed() {
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const [detections, setDetections] = useState([])
  const [videoSize, setVideoSize] = useState({ width: 0, height: 0 })
  const animationFrameRef = useRef(null)

  // Fetch detections periodically
  useEffect(() => {
    const fetchDetections = async () => {
      try {
        const response = await fetch(`${api.baseURL}/detections`)
        const data = await response.json()
        setDetections(data.detections || [])
      } catch (error) {
        // Silent fail - detections are optional
      }
    }

    const interval = setInterval(fetchDetections, 100) // 10 FPS detection updates
    return () => clearInterval(interval)
  }, [])

  // Update video size when image loads
  useEffect(() => {
    const img = videoRef.current
    if (!img) return

    const updateSize = () => {
      if (img.naturalWidth && img.naturalHeight) {
        setVideoSize({
          width: img.naturalWidth,
          height: img.naturalHeight
        })
      }
    }

    img.addEventListener('load', updateSize)
    updateSize()

    return () => img.removeEventListener('load', updateSize)
  }, [])

  // Draw bounding boxes on canvas
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    const container = canvas.parentElement

    const drawDetections = () => {
      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      if (detections.length === 0 || videoSize.width === 0) {
        animationFrameRef.current = requestAnimationFrame(drawDetections)
        return
      }

      // Calculate scaling
      const containerRect = container.getBoundingClientRect()
      const scaleX = containerRect.width / videoSize.width
      const scaleY = containerRect.height / videoSize.height
      const scale = Math.min(scaleX, scaleY)

      const scaledWidth = videoSize.width * scale
      const scaledHeight = videoSize.height * scale
      const offsetX = (containerRect.width - scaledWidth) / 2
      const offsetY = (containerRect.height - scaledHeight) / 2

      // Draw each detection
      detections.forEach(detection => {
        const bbox = detection.bbox
        const name = detection.name || 'Unknown'
        const status = detection.status || 'unknown'

        // Scale bounding box coordinates
        const x = bbox.x * scale + offsetX
        const y = bbox.y * scale + offsetY
        const width = bbox.width * scale
        const height = bbox.height * scale

        // Set color based on status
        let color
        if (status === 'friendly') {
          color = '#00ff00' // Green
        } else if (status === 'unknown') {
          color = '#ffa500' // Orange
        } else {
          color = '#ff0000' // Red
        }

        // Draw bounding box
        ctx.strokeStyle = color
        ctx.lineWidth = 3
        ctx.strokeRect(x, y, width, height)

        // Draw label background
        ctx.fillStyle = color
        const labelHeight = 35
        ctx.fillRect(x, y + height - labelHeight, width, labelHeight)

        // Draw text
        ctx.fillStyle = '#ffffff'
        ctx.font = 'bold 14px Arial'
        ctx.textBaseline = 'middle'
        
        // Draw name
        ctx.fillText(name, x + 6, y + height - labelHeight + 10)
        
        // Draw status
        ctx.font = '11px Arial'
        ctx.fillText(status.toUpperCase(), x + 6, y + height - labelHeight + 25)
      })

      animationFrameRef.current = requestAnimationFrame(drawDetections)
    }

    drawDetections()

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
    }
  }, [detections, videoSize])

  return (
    <div className="card">
      <h2 className="text-xl font-bold mb-4 flex items-center justify-between">
        <span>Live Feed</span>
        {detections.length > 0 && (
          <span className="text-sm font-normal text-green-500">
            {detections.length} face{detections.length !== 1 ? 's' : ''} detected
          </span>
        )}
      </h2>
      <div className="relative bg-black rounded-lg overflow-hidden" style={{ paddingBottom: '56.25%' }}>
        <img
          ref={videoRef}
          src={api.getVideoFeedUrl()}
          alt="Live video feed"
          className="absolute top-0 left-0 w-full h-full object-contain"
          crossOrigin="anonymous"
        />
        <canvas
          ref={canvasRef}
          className="absolute top-0 left-0 w-full h-full pointer-events-none"
          width={1920}
          height={1080}
        />
      </div>
    </div>
  )
}
