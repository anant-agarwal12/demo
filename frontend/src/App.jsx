import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import CommandCenter from './pages/CommandCenter'
import AlertsPage from './pages/AlertsPage'
import SettingsPage from './pages/SettingsPage'

function Navigation() {
  const location = useLocation()
  
  const isActive = (path) => location.pathname === path
  
  return (
    <nav className="bg-gray-800 text-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-8">
            <h1 className="text-2xl font-bold">?? DoggoBot</h1>
            <div className="flex space-x-4">
              <Link 
                to="/" 
                className={`px-3 py-2 rounded-md ${isActive('/') ? 'bg-gray-900' : 'hover:bg-gray-700'}`}
              >
                Command Center
              </Link>
              <Link 
                to="/alerts" 
                className={`px-3 py-2 rounded-md ${isActive('/alerts') ? 'bg-gray-900' : 'hover:bg-gray-700'}`}
              >
                Alerts
              </Link>
              <Link 
                to="/settings" 
                className={`px-3 py-2 rounded-md ${isActive('/settings') ? 'bg-gray-900' : 'hover:bg-gray-700'}`}
              >
                Settings
              </Link>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm">Online</span>
            </div>
            <span className="text-sm text-gray-400">Operator</span>
          </div>
        </div>
      </div>
    </nav>
  )
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <Navigation />
        <Routes>
          <Route path="/" element={<CommandCenter />} />
          <Route path="/alerts" element={<AlertsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
