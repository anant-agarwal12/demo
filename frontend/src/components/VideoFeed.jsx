import { useEffect, useRef, useState } from 'react'
import { api } from '../api/api'

export default function VideoFeed() {
  const containerRef = useRef(null)
  const imgRef = useRef(null)
  const canvasRef = useRef(null)
  const [boundingBoxes, setBoundingBoxes] = useState([])
  const [faceCount, setFaceCount] = useState(0)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const canvas = canvasRef.current
    const container = containerRef.current
    const img = imgRef.current

    if (!canvas || !container || !img) return

    // Function to draw bounding boxes
    const drawBoundingBoxes = () => {
      const ctx = canvas.getContext('2d')
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      if (!img.complete || boundingBoxes.length === 0) return

      // Get image dimensions and container dimensions
      const containerRect = container.getBoundingClientRect()
      const imgRect = img.getBoundingClientRect()

      // Calculate scaling factors
      const imgNaturalWidth = img.naturalWidth
      const imgNaturalHeight = img.naturalHeight
      const imgDisplayWidth = imgRect.width
      const imgDisplayHeight = imgRect.height

      // Calculate scale factors
      const scaleX = imgDisplayWidth / imgNaturalWidth
      const scaleY = imgDisplayHeight / imgNaturalHeight

      // Calculate offset (centered image)
      const offsetX = (containerRect.width - imgDisplayWidth) / 2
      const offsetY = (containerRect.height - imgDisplayHeight) / 2

      // Set canvas size to match container
      canvas.width = containerRect.width
      canvas.height = containerRect.height

      // Draw bounding boxes
      ctx.strokeStyle = '#00ff00'
      ctx.lineWidth = 3
      ctx.font = '16px Arial'
      ctx.fillStyle = '#00ff00'

      boundingBoxes.forEach((box, index) => {
        const left = box.left * scaleX + offsetX
        const top = box.top * scaleY + offsetY
        const width = (box.right - box.left) * scaleX
        const height = (box.bottom - box.top) * scaleY

        // Draw rectangle
        ctx.strokeRect(left, top, width, height)

        // Draw label background
        const label = box.name || `Face ${index + 1}`
        ctx.fillStyle = '#00ff00'
        const textMetrics = ctx.measureText(label)
        const textWidth = textMetrics.width
        const textHeight = 20

        ctx.fillRect(
          left,
          top - textHeight - 4,
          textWidth + 8,
          textHeight + 4
        )

        // Draw label text
        ctx.fillStyle = '#000000'
        ctx.fillText(label, left + 4, top - 6)
        ctx.fillStyle = '#00ff00'
      })
    }

    // Redraw when bounding boxes or image changes
    drawBoundingBoxes()

    // Also redraw on image load
    img.addEventListener('load', drawBoundingBoxes)
    window.addEventListener('resize', drawBoundingBoxes)

    return () => {
      img.removeEventListener('load', drawBoundingBoxes)
      window.removeEventListener('resize', drawBoundingBoxes)
    }
  }, [boundingBoxes])

  // Fetch bounding boxes periodically
  useEffect(() => {
    let intervalId

    const fetchFrameData = async () => {
      try {
        const data = await api.getFrameData()
        if (data.bounding_boxes) {
          setBoundingBoxes(data.bounding_boxes)
          setFaceCount(data.face_count || 0)
          setIsLoading(false)
        }
      } catch (error) {
        console.error('Error fetching frame data:', error)
      }
    }

    // Initial fetch
    fetchFrameData()

    // Poll every 100ms for real-time updates
    intervalId = setInterval(fetchFrameData, 100)

    return () => {
      if (intervalId) clearInterval(intervalId)
    }
  }, [])

  return (
    <div className="card">
      <h2 className="text-xl font-bold mb-4">
        Live Feed
        {faceCount > 0 && (
          <span className="ml-2 text-green-500 text-base">
            ({faceCount} {faceCount === 1 ? 'face' : 'faces'} detected)
          </span>
        )}
      </h2>
      <div
        ref={containerRef}
        className="relative bg-black rounded-lg overflow-hidden"
        style={{ paddingBottom: '56.25%' }}
      >
        <img
          ref={imgRef}
          src={api.getVideoFeedUrl()}
          alt="Live video feed"
          className="absolute top-0 left-0 w-full h-full object-contain"
          onLoad={() => setIsLoading(false)}
        />
        <canvas
          ref={canvasRef}
          className="absolute top-0 left-0 w-full h-full pointer-events-none"
          style={{ zIndex: 10 }}
        />
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">
            <p className="text-white">Loading video feed...</p>
          </div>
        )}
      </div>
    </div>
  )
}
