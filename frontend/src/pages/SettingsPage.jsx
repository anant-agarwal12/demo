import { useState, useEffect } from 'react'
import { api } from '../api/api'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('whitelist')
  const [whitelist, setWhitelist] = useState([])
  const [loading, setLoading] = useState(false)
  const [newPersonName, setNewPersonName] = useState('')
  const [newPersonImages, setNewPersonImages] = useState([])
  const [apiKey, setApiKey] = useState('doggobot-secret-key-change-me')

  useEffect(() => {
    if (activeTab === 'whitelist') {
      loadWhitelist()
    }
  }, [activeTab])

  const loadWhitelist = async () => {
    setLoading(true)
    try {
      const data = await api.getWhitelist()
      setWhitelist(data.whitelist || [])
    } catch (err) {
      console.error('Error loading whitelist:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleAddPerson = async (e) => {
    e.preventDefault()
    if (!newPersonName || newPersonImages.length === 0) {
      alert('Please provide a name and at least one image')
      return
    }

    setLoading(true)
    try {
      await api.addToWhitelist(newPersonName, newPersonImages)
      alert('Person added to whitelist successfully!')
      setNewPersonName('')
      setNewPersonImages([])
      loadWhitelist()
    } catch (err) {
      console.error('Error adding person:', err)
      alert('Error adding person to whitelist')
    } finally {
      setLoading(false)
    }
  }

  const handleRefreshWhitelist = async () => {
    setLoading(true)
    try {
      const result = await api.refreshWhitelist()
      alert(result.message)
    } catch (err) {
      console.error('Error refreshing whitelist:', err)
      alert('Error refreshing whitelist')
    } finally {
      setLoading(false)
    }
  }

  const handleImageSelect = (e) => {
    const files = Array.from(e.target.files)
    setNewPersonImages(files)
  }

  return (
    <div className="container mx-auto px-4 py-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Settings</h1>
        <p className="text-gray-600">Configure DoggoBot system settings</p>
      </div>

      {/* Tabs */}
      <div className="flex space-x-4 mb-6 border-b">
        <button
          onClick={() => setActiveTab('whitelist')}
          className={`px-4 py-2 font-semibold ${
            activeTab === 'whitelist'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-600'
          }`}
        >
          Whitelist Management
        </button>
        <button
          onClick={() => setActiveTab('api')}
          className={`px-4 py-2 font-semibold ${
            activeTab === 'api'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-600'
          }`}
        >
          API Settings
        </button>
        <button
          onClick={() => setActiveTab('thresholds')}
          className={`px-4 py-2 font-semibold ${
            activeTab === 'thresholds'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-600'
          }`}
        >
          Thresholds
        </button>
      </div>

      {/* Whitelist Management Tab */}
      {activeTab === 'whitelist' && (
        <div className="space-y-6">
          {/* Add Person Form */}
          <div className="card">
            <h2 className="text-xl font-bold mb-4">Add Person to Whitelist</h2>
            <form onSubmit={handleAddPerson} className="space-y-4">
              <div>
                <label className="block text-sm font-semibold mb-2">Name</label>
                <input
                  type="text"
                  value={newPersonName}
                  onChange={(e) => setNewPersonName(e.target.value)}
                  placeholder="Enter person's name"
                  className="input w-full"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2">
                  Images (multiple recommended)
                </label>
                <input
                  type="file"
                  accept="image/*"
                  multiple
                  onChange={handleImageSelect}
                  className="input w-full"
                  required
                />
                {newPersonImages.length > 0 && (
                  <p className="text-sm text-gray-600 mt-2">
                    {newPersonImages.length} image(s) selected
                  </p>
                )}
              </div>

              <button
                type="submit"
                disabled={loading}
                className="btn-primary"
              >
                {loading ? 'Adding...' : 'Add Person'}
              </button>
            </form>
          </div>

          {/* Whitelist Table */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">Current Whitelist</h2>
              <div className="flex gap-2">
                <button
                  onClick={loadWhitelist}
                  disabled={loading}
                  className="btn-secondary"
                >
                  {loading ? 'Loading...' : 'Refresh'}
                </button>
                <button
                  onClick={handleRefreshWhitelist}
                  disabled={loading}
                  className="btn-primary"
                >
                  Refresh Encodings
                </button>
              </div>
            </div>

            {loading ? (
              <p className="text-center py-8 text-gray-600">Loading...</p>
            ) : whitelist.length === 0 ? (
              <p className="text-center py-8 text-gray-400">No people in whitelist</p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {whitelist.map(person => (
                  <div key={person.id} className="border rounded-lg p-4">
                    <h3 className="font-bold mb-2">{person.name}</h3>
                    <p className="text-sm text-gray-600 mb-3">
                      {person.enc_count} sample image(s)
                    </p>
                    {person.sample_images && person.sample_images.length > 0 && (
                      <div className="grid grid-cols-3 gap-2">
                        {person.sample_images.slice(0, 3).map((img, idx) => (
                          <img
                            key={idx}
                            src={`${API_BASE}/${img}`}
                            alt={`${person.name} ${idx + 1}`}
                            className="w-full h-20 object-cover rounded"
                          />
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* API Settings Tab */}
      {activeTab === 'api' && (
        <div className="card">
          <h2 className="text-xl font-bold mb-4">API Configuration</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold mb-2">API Key</label>
              <input
                type="text"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                className="input w-full font-mono"
                readOnly
              />
              <p className="text-sm text-gray-600 mt-2">
                Use this API key in the X-API-KEY header for /frame and /alert endpoints
              </p>
            </div>

            <div>
              <label className="block text-sm font-semibold mb-2">Backend URL</label>
              <input
                type="text"
                value={API_BASE}
                className="input w-full font-mono"
                readOnly
              />
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <p className="text-sm text-yellow-800">
                ?? <strong>Note:</strong> To change the API key, update the API_KEY environment variable 
                in the backend .env file and restart the server.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Thresholds Tab */}
      {activeTab === 'thresholds' && (
        <div className="card">
          <h2 className="text-xl font-bold mb-4">Detection Thresholds</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold mb-2">
                Face Match Threshold
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                defaultValue="0.6"
                className="w-full"
              />
              <p className="text-sm text-gray-600">
                Minimum confidence for face recognition (default: 0.6)
              </p>
            </div>

            <div>
              <label className="block text-sm font-semibold mb-2">
                Loitering Time (seconds)
              </label>
              <input
                type="number"
                defaultValue="30"
                className="input w-full"
              />
              <p className="text-sm text-gray-600">
                Time before marking as suspicious (default: 30s)
              </p>
            </div>

            <div>
              <label className="block text-sm font-semibold mb-2">
                Detection Distance Limit (meters)
              </label>
              <input
                type="number"
                defaultValue="10"
                className="input w-full"
              />
              <p className="text-sm text-gray-600">
                Maximum detection range (default: 10m)
              </p>
            </div>

            <button className="btn-primary">
              Save Thresholds
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
