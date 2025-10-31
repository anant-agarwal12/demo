import { useState, useRef, useEffect } from 'react'

export default function WebcamCapture({ onCapture, onClose }) {
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const [stream, setStream] = useState(null)
  const [capturedImages, setCapturedImages] = useState([])
  const [isCapturing, setIsCapturing] = useState(false)
  const [error, setError] = useState(null)
  const [cameraStarted, setCameraStarted] = useState(false)

  const startCamera = async () => {
    try {
      setError(null)
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user'
        }
      })
      
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream
      }
      
      setStream(mediaStream)
      setCameraStarted(true)
    } catch (err) {
      console.error('Error accessing camera:', err)
      setError('Could not access camera. Please ensure camera permissions are granted.')
    }
  }

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      setStream(null)
      setCameraStarted(false)
    }
  }

  const captureImage = () => {
    if (!videoRef.current || !canvasRef.current) return

    const video = videoRef.current
    const canvas = canvasRef.current
    
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    
    const ctx = canvas.getContext('2d')
    ctx.drawImage(video, 0, 0)
    
    canvas.toBlob((blob) => {
      if (blob) {
        const file = new File([blob], `capture_${Date.now()}.jpg`, { type: 'image/jpeg' })
        setCapturedImages(prev => [...prev, { file, url: URL.createObjectURL(blob) }])
      }
    }, 'image/jpeg', 0.95)
  }

  const removeImage = (index) => {
    setCapturedImages(prev => {
      const newImages = [...prev]
      URL.revokeObjectURL(newImages[index].url)
      newImages.splice(index, 1)
      return newImages
    })
  }

  const handleDone = () => {
    const files = capturedImages.map(img => img.file)
    onCapture(files)
    stopCamera()
  }

  const handleCancel = () => {
    capturedImages.forEach(img => URL.revokeObjectURL(img.url))
    stopCamera()
    onClose()
  }

  useEffect(() => {
    startCamera()
    
    return () => {
      stopCamera()
      capturedImages.forEach(img => URL.revokeObjectURL(img.url))
    }
  }, [])

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold">Capture Photos</h2>
            <button
              onClick={handleCancel}
              className="text-gray-500 hover:text-gray-700 text-2xl"
            >
              ×
            </button>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          {!error && (
            <>
              <div className="relative bg-black rounded-lg overflow-hidden mb-4">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  className="w-full h-auto"
                  style={{ maxHeight: '400px' }}
                />
                
                {cameraStarted && (
                  <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2">
                    <button
                      onClick={captureImage}
                      disabled={isCapturing}
                      className="bg-white hover:bg-gray-100 text-gray-800 font-bold py-3 px-6 rounded-full shadow-lg transition-all"
                    >
                      📸 Capture Photo
                    </button>
                  </div>
                )}
                
                {!cameraStarted && (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-white text-center">
                      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-2"></div>
                      <p>Starting camera...</p>
                    </div>
                  </div>
                )}
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                <p className="text-sm text-blue-800">
                  <strong>💡 Tips for best results:</strong>
                  <ul className="list-disc list-inside mt-2 space-y-1">
                    <li>Capture 3-5 photos from different angles</li>
                    <li>Ensure good lighting and face is clearly visible</li>
                    <li>Try different expressions (neutral, smiling)</li>
                    <li>Keep face centered in the frame</li>
                  </ul>
                </p>
              </div>

              {capturedImages.length > 0 && (
                <div className="mb-4">
                  <h3 className="font-semibold mb-2">
                    Captured Photos ({capturedImages.length})
                  </h3>
                  <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-2">
                    {capturedImages.map((img, index) => (
                      <div key={index} className="relative group">
                        <img
                          src={img.url}
                          alt={`Capture ${index + 1}`}
                          className="w-full h-24 object-cover rounded border-2 border-green-500"
                        />
                        <button
                          onClick={() => removeImage(index)}
                          className="absolute top-1 right-1 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          ×
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex justify-end gap-2">
                <button
                  onClick={handleCancel}
                  className="btn-secondary"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDone}
                  disabled={capturedImages.length === 0}
                  className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Use {capturedImages.length} Photo{capturedImages.length !== 1 ? 's' : ''}
                </button>
              </div>
            </>
          )}
        </div>
      </div>

      <canvas ref={canvasRef} style={{ display: 'none' }} />
    </div>
  )
}