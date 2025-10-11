import React, { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'

const Profile = () => {
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState(false)
  const [upgrading, setUpgrading] = useState(false)
  const [preferences, setPreferences] = useState({
    remote_option: '',
    company_size: '',
    industry: ''
  })
  const { token, user } = useAuth()

  useEffect(() => {
    fetchProfile()
  }, [])

  const fetchProfile = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/profile', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data = await response.json()
      setProfile(data.profile)
      setPreferences(data.profile.preferences || {})
    } catch (err) {
      console.error('Error fetching profile:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleUpdatePreferences = async (e) => {
    e.preventDefault()
    setUpdating(true)

    try {
      const response = await fetch('http://localhost:8000/api/profile', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ preferences })
      })

      if (response.ok) {
        alert('Preferences updated successfully!')
        fetchProfile()
      }
    } catch (err) {
      alert('Error updating preferences')
    } finally {
      setUpdating(false)
    }
  }

  const handleUpgradeToPremium = async () => {
    setUpgrading(true)
    try {
      const response = await fetch('http://localhost:8000/api/premium/upgrade', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        alert('Successfully upgraded to Premium!')
        window.location.reload()
      }
    } catch (err) {
      alert('Error upgrading to premium')
    } finally {
      setUpgrading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <div className="inline-block mb-4">
            <div className="relative w-24 h-24">
              <div className="absolute inset-0 animate-spin" style={{ animationDuration: '2s' }}>
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-6 h-6 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full shadow-lg"></div>
              </div>
              <div className="absolute inset-0 animate-spin" style={{ animationDuration: '2s', animationDelay: '0.33s' }}>
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-6 h-6 bg-gradient-to-br from-purple-500 to-purple-600 rounded-full shadow-lg"></div>
              </div>
              <div className="absolute inset-0 animate-spin" style={{ animationDuration: '2s', animationDelay: '0.66s' }}>
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-6 h-6 bg-gradient-to-br from-pink-500 to-pink-600 rounded-full shadow-lg"></div>
              </div>
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-3 h-3 bg-white rounded-full animate-pulse shadow-xl"></div>
              </div>
            </div>
          </div>
          <p className="text-gray-700 font-medium text-lg animate-pulse">Loading your profile...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto animate-fadeIn">
      <div className="mb-8 bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          Your Profile
        </h1>
        <p className="text-gray-600 mt-2 text-lg">👤 Manage your account and preferences</p>
      </div>

      <div className="grid gap-6">
        {/* User Info */}
        <div className="bg-gradient-to-br from-white to-blue-50 rounded-2xl shadow-xl p-8 border-2 border-blue-100">
          <div className="flex items-center space-x-4 mb-6">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-2xl shadow-lg">
              {user.full_name?.charAt(0).toUpperCase()}
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">User Information</h2>
              <p className="text-gray-600">Your account details</p>
            </div>
          </div>
          <div className="space-y-4">
            <div className="bg-white rounded-xl p-4 shadow-sm">
              <p className="text-sm text-gray-500 font-medium mb-1">Full Name</p>
              <p className="font-bold text-gray-900 text-lg">{user.full_name}</p>
            </div>
            <div className="bg-white rounded-xl p-4 shadow-sm">
              <p className="text-sm text-gray-500 font-medium mb-1">Email Address</p>
              <p className="font-bold text-gray-900 text-lg">{user.email}</p>
            </div>
            <div className="bg-white rounded-xl p-4 shadow-sm">
              <p className="text-sm text-gray-500 font-medium mb-1">Account Type</p>
              <div className="mt-2">
                {user.is_premium ? (
                  <span className="bg-gradient-to-r from-yellow-400 to-yellow-500 text-white px-4 py-2 rounded-full font-bold inline-flex items-center space-x-2 shadow-md">
                    <span>⭐</span>
                    <span>Premium Member</span>
                  </span>
                ) : (
                  <span className="bg-gray-100 text-gray-700 px-4 py-2 rounded-full font-bold inline-flex items-center space-x-2">
                    <span>🆓</span>
                    <span>Free Account</span>
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Resume Info */}
        <div className="bg-gradient-to-br from-white to-purple-50 rounded-2xl shadow-xl p-8 border-2 border-purple-100">
          <div className="flex items-center space-x-3 mb-6">
            <span className="text-4xl">📄</span>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Resume & Skills</h2>
              <p className="text-gray-600">Your professional profile</p>
            </div>
          </div>
          {profile.has_resume ? (
            <div className="space-y-4">
              <div className="bg-white rounded-xl p-5 shadow-sm">
                <p className="text-sm text-gray-500 font-medium mb-3">
                  💼 Skills ({profile.skills?.length || 0} total)
                </p>
                <div className="flex flex-wrap gap-2">
                  {profile.skills?.slice(0, 15).map((skill, idx) => (
                    <span key={idx} className="bg-gradient-to-r from-blue-100 to-purple-100 text-blue-800 px-3 py-2 rounded-lg text-sm font-semibold shadow-sm">
                      {skill}
                    </span>
                  ))}
                  {profile.skills?.length > 15 && (
                    <span className="text-gray-500 text-sm font-medium px-3 py-2">
                      +{profile.skills.length - 15} more
                    </span>
                  )}
                </div>
              </div>
              {profile.experience_years && (
                <div className="bg-white rounded-xl p-5 shadow-sm">
                  <p className="text-sm text-gray-500 font-medium mb-2">🎯 Experience Level</p>
                  <p className="font-bold text-gray-900 text-xl">{profile.experience_years} years</p>
                </div>
              )}
              {profile.education_level && (
                <div className="bg-white rounded-xl p-5 shadow-sm">
                  <p className="text-sm text-gray-500 font-medium mb-2">🎓 Education</p>
                  <p className="font-bold text-gray-900 text-xl capitalize">{profile.education_level}</p>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-white rounded-xl p-8 text-center shadow-sm">
              <div className="text-5xl mb-3">📭</div>
              <p className="text-gray-600 font-medium">No resume uploaded yet</p>
              <p className="text-gray-500 text-sm mt-2">Upload your resume from the Dashboard to get started</p>
            </div>
          )}
        </div>

        {/* Preferences */}
        <div className="bg-gradient-to-br from-white to-green-50 rounded-2xl shadow-xl p-8 border-2 border-green-100">
          <div className="flex items-center space-x-3 mb-6">
            <span className="text-4xl">⚙️</span>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Job Preferences</h2>
              <p className="text-gray-600">Customize your job search</p>
            </div>
          </div>
          <form onSubmit={handleUpdatePreferences} className="space-y-5">
            <div className="bg-white rounded-xl p-5 shadow-sm">
              <label className="block text-sm font-bold text-gray-700 mb-3 flex items-center space-x-2">
                <span>🏠</span>
                <span>Remote Work Preference</span>
              </label>
              <select
                value={preferences.remote_option || ''}
                onChange={(e) => setPreferences({...preferences, remote_option: e.target.value})}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all font-medium"
              >
                <option value="">No preference</option>
                <option value="remote">🌍 Remote</option>
                <option value="hybrid">🔄 Hybrid</option>
                <option value="onsite">🏢 Onsite</option>
              </select>
            </div>

            <div className="bg-white rounded-xl p-5 shadow-sm">
              <label className="block text-sm font-bold text-gray-700 mb-3 flex items-center space-x-2">
                <span>🏭</span>
                <span>Company Size Preference</span>
              </label>
              <select
                value={preferences.company_size || ''}
                onChange={(e) => setPreferences({...preferences, company_size: e.target.value})}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all font-medium"
              >
                <option value="">No preference</option>
                <option value="startup">🚀 Startup (1-50)</option>
                <option value="small">📦 Small (51-200)</option>
                <option value="medium">🏪 Medium (201-1000)</option>
                <option value="large">🏬 Large (1001-5000)</option>
                <option value="enterprise">🏛️ Enterprise (5000+)</option>
              </select>
            </div>

            <div className="bg-white rounded-xl p-5 shadow-sm">
              <label className="block text-sm font-bold text-gray-700 mb-3 flex items-center space-x-2">
                <span>🎯</span>
                <span>Industry Preference</span>
              </label>
              <input
                type="text"
                value={preferences.industry || ''}
                onChange={(e) => setPreferences({...preferences, industry: e.target.value})}
                placeholder="e.g., technology, finance, healthcare"
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all font-medium"
              />
            </div>

            <button
              type="submit"
              disabled={updating}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-4 rounded-xl hover:shadow-xl transition-shadow font-bold text-lg disabled:opacity-50 flex items-center justify-center space-x-2"
            >
              {updating ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Updating...</span>
                </>
              ) : (
                <>
                  <span>💾</span>
                  <span>Save Preferences</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Premium Upgrade */}
        {!user.is_premium && (
          <div className="bg-gradient-to-br from-yellow-50 via-yellow-100 to-orange-100 rounded-2xl shadow-2xl p-8 border-4 border-yellow-300 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-yellow-300 rounded-full -mr-16 -mt-16 opacity-20"></div>
            <div className="absolute bottom-0 left-0 w-24 h-24 bg-orange-300 rounded-full -ml-12 -mb-12 opacity-20"></div>
            <div className="relative">
              <div className="flex items-center space-x-3 mb-4">
                <span className="text-5xl">⭐</span>
                <div>
                  <h2 className="text-3xl font-black text-gray-900">Upgrade to Premium</h2>
                  <p className="text-yellow-800 font-bold text-lg">Unlock your full potential</p>
                </div>
              </div>
              <div className="bg-white/80 backdrop-blur rounded-xl p-5 mb-6">
                <p className="text-gray-900 font-bold text-2xl mb-2">
                  Only <span className="text-yellow-600">$9.99</span>/month
                </p>
                <p className="text-gray-600">Cancel anytime, no commitments</p>
              </div>
              <ul className="space-y-3 mb-8">
                <li className="flex items-start text-gray-800 bg-white/60 backdrop-blur rounded-lg p-3">
                  <span className="text-green-600 mr-3 text-xl font-bold">✓</span>
                  <span className="font-semibold">Detailed salary predictions with percentiles</span>
                </li>
                <li className="flex items-start text-gray-800 bg-white/60 backdrop-blur rounded-lg p-3">
                  <span className="text-green-600 mr-3 text-xl font-bold">✓</span>
                  <span className="font-semibold">Company-fit score explanations</span>
                </li>
                <li className="flex items-start text-gray-800 bg-white/60 backdrop-blur rounded-lg p-3">
                  <span className="text-green-600 mr-3 text-xl font-bold">✓</span>
                  <span className="font-semibold">Skill gap analysis and recommendations</span>
                </li>
                <li className="flex items-start text-gray-800 bg-white/60 backdrop-blur rounded-lg p-3">
                  <span className="text-green-600 mr-3 text-xl font-bold">✓</span>
                  <span className="font-semibold">Unlimited job searches</span>
                </li>
              </ul>
              <button
                onClick={handleUpgradeToPremium}
                disabled={upgrading}
                className="w-full bg-gradient-to-r from-yellow-500 to-orange-500 text-white px-8 py-5 rounded-xl hover:shadow-xl transition-shadow font-black text-xl disabled:opacity-50 flex items-center justify-center space-x-3"
              >
                {upgrading ? (
                  <>
                    <div className="w-6 h-6 border-3 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <span>⭐</span>
                    <span>Upgrade Now</span>
                    <span>→</span>
                  </>
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Profile
