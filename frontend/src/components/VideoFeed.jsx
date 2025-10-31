import { api } from '../api/api'

export default function VideoFeed() {
  return (
    <div className="card">
      <h2 className="text-xl font-bold mb-4">Live Feed</h2>
      <div className="relative bg-black rounded-lg overflow-hidden" style={{ paddingBottom: '56.25%' }}>
        <img
          src={api.getVideoFeedUrl()}
          alt="Live video feed"
          className="absolute top-0 left-0 w-full h-full object-contain"
        />
      </div>
    </div>
  )
}
