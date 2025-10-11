import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Loader, JobCardSkeleton } from '../components/Loader'

const Dashboard = () => {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [hasResume, setHasResume] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploadSuccess, setUploadSuccess] = useState(false)
  const { token, user } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    checkProfile()
  }, [])

  const checkProfile = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/profile', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data = await response.json()
      setHasResume(data.profile.has_resume)
      
      if (data.profile.has_resume) {
        fetchRecommendations()
      } else {
        setLoading(false)
      }
    } catch (err) {
      setError('Error loading profile')
      setLoading(false)
    }
  }

  const fetchRecommendations = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/jobs/recommendations?top_k=10', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data = await response.json()
      setJobs(data.matches || [])
    } catch (err) {
      setError('Error loading recommendations')
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    setUploading(true)
    setError('')
    setUploadSuccess(false)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('http://localhost:8000/api/resumes/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      })

      if (response.ok) {
        setUploadSuccess(true)
        setHasResume(true)
        setLoading(true)
        setTimeout(() => {
          fetchRecommendations()
        }, 500)
      } else {
        const data = await response.json()
        setError(data.detail || 'Upload failed')
      }
    } catch (err) {
      setError('Network error during upload')
    } finally {
      setUploading(false)
    }
  }

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-gray-600'
  }

  const getScoreBgColor = (score) => {
    if (score >= 80) return 'bg-green-50 border-green-200'
    if (score >= 60) return 'bg-yellow-50 border-yellow-200'
    return 'bg-gray-50 border-gray-200'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader size="lg" text="Loading your dashboard..." />
      </div>
    )
  }

  if (!hasResume) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl shadow-xl p-12 text-center">
          <div className="w-20 h-20 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6">
            <span className="text-4xl">📄</span>
          </div>
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Upload Your Resume
          </h2>
          <p className="text-gray-600 mb-8 text-lg">
            Get started by uploading your resume to receive AI-powered job recommendations
          </p>
          <label className="inline-block">
            <input
              type="file"
              accept=".pdf,.docx"
              onChange={handleFileUpload}
              className="hidden"
              disabled={uploading}
            />
            <span className="cursor-pointer bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-xl text-lg font-semibold hover:shadow-2xl transform hover:-translate-y-1 transition-all inline-block">
              {uploading ? '⏳ Uploading...' : '📤 Choose File (PDF or DOCX)'}
            </span>
          </label>
          {error && (
            <div className="mt-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}
          <p className="mt-6 text-sm text-gray-500">
            Supported formats: PDF, DOCX • Max size: 5MB
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="animate-fadeIn">
      <div className="mb-8 flex flex-col md:flex-row md:justify-between md:items-center gap-4 bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Job Recommendations
          </h1>
          <p className="text-gray-600 mt-2 text-lg">✨ AI-powered matches tailored for you</p>
        </div>
        <label className="cursor-pointer group">
          <input
            type="file"
            accept=".pdf,.docx"
            onChange={handleFileUpload}
            className="hidden"
            disabled={uploading}
          />
          <span className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-xl hover:shadow-xl transform hover:-translate-y-1 transition-all inline-flex items-center space-x-2 font-semibold">
            <span>📤</span>
            <span>{uploading ? 'Uploading...' : 'Update Resume'}</span>
          </span>
        </label>
      </div>

      {uploadSuccess && (
        <div className="bg-green-50 border-2 border-green-300 text-green-800 px-6 py-4 rounded-xl mb-6 flex items-center space-x-3 animate-slideIn shadow-lg">
          <span className="text-2xl">✅</span>
          <span className="font-semibold">Resume uploaded successfully! Generating recommendations...</span>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border-2 border-red-300 text-red-700 px-6 py-4 rounded-xl mb-6 flex items-center space-x-3 animate-slideIn shadow-lg">
          <span className="text-2xl">⚠️</span>
          <span className="font-semibold">{error}</span>
        </div>
      )}

      {loading ? (
        <div className="grid gap-6">
          <JobCardSkeleton />
          <JobCardSkeleton />
          <JobCardSkeleton />
        </div>
      ) : jobs.length === 0 ? (
        <div className="bg-gradient-to-br from-gray-50 to-blue-50 rounded-2xl shadow-xl p-16 text-center border-2 border-gray-200">
          <div className="text-8xl mb-6 animate-bounce">🔍</div>
          <h3 className="text-2xl font-bold text-gray-900 mb-3">No Matches Yet</h3>
          <p className="text-gray-600 text-lg max-w-md mx-auto">
            We're still analyzing your profile. Try updating your resume or adjusting your preferences for better matches.
          </p>
        </div>
      ) : (
        <div className="grid gap-6">
          {jobs.map((match, index) => (
            <div
              key={match.job.id}
              className="bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 p-6 cursor-pointer border-2 border-transparent hover:border-blue-300 transform hover:-translate-y-2 animate-fadeIn"
              style={{ animationDelay: `${index * 100}ms` }}
              onClick={() => navigate(`/jobs/${match.job.id}`)}
            >
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <h3 className="text-2xl font-bold text-gray-900 mb-1">{match.job.title}</h3>
                  <p className="text-lg text-gray-700 font-semibold">{match.job.company}</p>
                  <div className="flex items-center space-x-3 mt-2 text-sm text-gray-500">
                    <span className="flex items-center">
                      <span className="mr-1">📍</span>
                      {match.job.location}
                    </span>
                    <span className="flex items-center">
                      <span className="mr-1">💼</span>
                      {match.job.remote_option}
                    </span>
                  </div>
                </div>
                <div className="text-right ml-4">
                  <div className={`text-4xl font-bold ${getScoreColor(match.compatibility_score)} mb-1`}>
                    {match.compatibility_score}%
                  </div>
                  <p className="text-sm text-gray-500 font-semibold">Match Score</p>
                </div>
              </div>

              {match.job.salary_min && match.job.salary_max && (
                <div className="bg-green-50 border border-green-200 rounded-lg px-4 py-2 mb-4 inline-block">
                  <p className="text-green-800 font-semibold">
                    💰 ${match.job.salary_min.toLocaleString()} - ${match.job.salary_max.toLocaleString()}
                  </p>
                </div>
              )}

              {match.matching_skills && match.matching_skills.length > 0 && (
                <div className="mb-4">
                  <p className="text-sm text-gray-600 mb-2 font-semibold">✅ Matching Skills:</p>
                  <div className="flex flex-wrap gap-2">
                    {match.matching_skills.slice(0, 6).map((skill, idx) => (
                      <span key={idx} className="bg-gradient-to-r from-green-100 to-green-200 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                        {skill}
                      </span>
                    ))}
                    {match.matching_skills.length > 6 && (
                      <span className="text-gray-500 text-sm">+{match.matching_skills.length - 6} more</span>
                    )}
                  </div>
                </div>
              )}

              {match.company_fit_score && (
                <div className="mt-4 pt-4 border-t border-gray-200 flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span>🏢</span>
                    <span className="text-sm text-gray-600">Company Fit:</span>
                    <span className="font-bold text-purple-600">{match.company_fit_score}%</span>
                  </div>
                  <span className="text-blue-600 text-sm font-semibold">View Details →</span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Dashboard
