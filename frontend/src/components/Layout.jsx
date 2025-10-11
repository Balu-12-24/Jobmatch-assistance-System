import React, { useState, useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const Layout = ({ children }) => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [showMenu, setShowMenu] = useState(false)
  const [isNavigating, setIsNavigating] = useState(false)

  useEffect(() => {
    setIsNavigating(false)
  }, [location])

  const handleLogout = () => {
    setIsNavigating(true)
    logout()
    navigate('/login')
  }

  const handleNavigation = (path) => {
    if (location.pathname !== path) {
      setIsNavigating(true)
      navigate(path)
    }
  }

  const isActive = (path) => location.pathname === path

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50">
      {/* Navigation Loading Bar */}
      {isNavigating && (
        <div className="fixed top-0 left-0 right-0 z-[100]">
          <div className="h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 animate-pulse"></div>
          <div className="h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 animate-[slideRight_1s_ease-in-out_infinite]"></div>
        </div>
      )}

      <nav className="bg-white/98 backdrop-blur-2xl shadow-2xl sticky top-0 z-50 border-b border-gray-200/50">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            {/* Logo Section */}
            <div className="flex items-center space-x-8">
              <button 
                onClick={() => handleNavigation('/dashboard')}
                className="flex items-center space-x-3 group"
              >
                <div className="w-12 h-12 bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 rounded-2xl flex items-center justify-center shadow-lg">
                  <span className="text-white font-black text-2xl">J</span>
                </div>
                <div className="flex flex-col">
                  <span className="text-2xl font-black bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent leading-none">
                    JobMatch AI
                  </span>
                  <span className="text-xs text-gray-500 font-medium mt-0.5">AI-Powered Job Matching</span>
                </div>
              </button>
              
              {/* Navigation Links */}
              {user && (
                <div className="hidden md:flex items-center space-x-2">
                  <button
                    onClick={() => handleNavigation('/dashboard')}
                    className={`px-6 py-2.5 rounded-xl font-bold transition-all flex items-center space-x-2 ${
                      isActive('/dashboard')
                        ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                        : 'text-gray-700 hover:bg-blue-50 hover:text-blue-600'
                    }`}
                  >
                    <span className="text-lg">🎯</span>
                    <span>Dashboard</span>
                  </button>
                  
                  <button
                    onClick={() => handleNavigation('/profile')}
                    className={`px-6 py-2.5 rounded-xl font-bold transition-all flex items-center space-x-2 ${
                      isActive('/profile')
                        ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                        : 'text-gray-700 hover:bg-blue-50 hover:text-blue-600'
                    }`}
                  >
                    <span className="text-lg">👤</span>
                    <span>Profile</span>
                  </button>
                </div>
              )}
            </div>

            {/* Right Section */}
            {user && (
              <div className="flex items-center space-x-4">
                {/* Premium Badge */}
                {user.is_premium ? (
                  <span className="bg-gradient-to-r from-yellow-400 via-yellow-500 to-orange-500 text-white px-6 py-2.5 rounded-full text-sm font-black shadow-lg flex items-center space-x-2">
                    <span className="text-lg">⭐</span>
                    <span>Premium</span>
                  </span>
                ) : (
                  <button
                    onClick={() => handleNavigation('/profile')}
                    className="bg-gradient-to-r from-yellow-400 via-yellow-500 to-orange-500 text-white px-6 py-2.5 rounded-full text-sm font-black shadow-lg hover:shadow-xl transition-shadow flex items-center space-x-2"
                  >
                    <span className="text-lg">⭐</span>
                    <span>Upgrade</span>
                  </button>
                )}

                {/* User Menu */}
                <div className="relative">
                  <button
                    onClick={() => setShowMenu(!showMenu)}
                    className="w-12 h-12 bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 rounded-full flex items-center justify-center text-white font-black text-lg shadow-lg ring-2 ring-white"
                  >
                    {user.full_name?.charAt(0).toUpperCase()}
                  </button>
                  
                  {showMenu && (
                    <div className="absolute right-0 mt-4 w-72 bg-white rounded-2xl shadow-2xl border border-gray-100 overflow-hidden animate-slideDown">
                      <div className="bg-gradient-to-br from-blue-50 to-purple-50 px-6 py-4 border-b border-gray-200">
                        <div className="flex items-center space-x-3">
                          <div className="w-12 h-12 bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 rounded-full flex items-center justify-center text-white font-black text-lg shadow-lg">
                            {user.full_name?.charAt(0).toUpperCase()}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="font-bold text-gray-900 text-lg truncate">{user.full_name}</p>
                            <p className="text-sm text-gray-600 truncate">{user.email}</p>
                          </div>
                        </div>
                      </div>
                      
                      <div className="p-2">
                        <button
                          onClick={handleLogout}
                          className="w-full text-left px-4 py-3 text-red-600 hover:bg-red-50 rounded-xl transition-colors font-bold flex items-center space-x-3"
                        >
                          <span className="text-xl">🚪</span>
                          <span>Logout</span>
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  )
}

export default Layout
