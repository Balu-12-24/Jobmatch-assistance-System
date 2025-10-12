import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Loader, JobCardSkeleton } from '../components/Loader'
import ResumeAnalysisCard from '../components/ResumeAnalysisCard'
import FilterPanel from '../components/FilterPanel'
import JobCard from '../components/JobCard'

const Dashboard = () => {
  const [jobs, setJobs] = useState([])
  const [filteredJobs, setFilteredJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [hasResume, setHasResume] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploadSuccess, setUploadSuccess] = useState(false)
  const [resumeAnalysis, setResumeAnalysis] = useState(null)
  const [savedJobs, setSavedJobs] = useState(new Set())
  const [showFilters, setShowFilters] = useState(false)
  const [filters, setFilters] = useState({
    minScore: 0,
    location: '',
    salaryMin: 0,
    salaryMax: 10000000,
    companyType: '',
    remoteOption: '',
    sortBy: 'compatibility'
  })
  const { token, user } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    checkProfile()
    fetchSavedJobs()
  }, [])

  useEffect(() => {
    applyFilters()
  }, [jobs, filters])

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
        fetchResumeAnalysis()
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
      const response = await fetch('http://localhost:8000/api/jobs/recommendations?top_k=20', {
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

  const fetchResumeAnalysis = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/resumes/analysis', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      if (response.ok) {
        const data = await response.json()
        setResumeAnalysis(data)
      }
    } catch (err) {
      console.error('Error fetching resume analysis:', err)
    }
  }

  const fetchSavedJobs = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/jobs/saved', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      if (response.ok) {
        const data = await response.json()
        setSavedJobs(new Set(data.saved_jobs.map(j => j.job_id)))
      }
    } catch (err) {
      console.error('Error fetching saved jobs:', err)
    }
  }

  const handleSaveJob = async (jobId) => {
    try {
      const response = await fetch('http://localhost:8000/api/jobs/save', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ job_id: jobId })
      })
      
      if (response.ok) {
        setSavedJobs(prev => new Set([...prev, jobId]))
      }
    } catch (err) {
      console.error('Error saving job:', err)
    }
  }

  const handleUnsaveJob = async (jobId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/jobs/save/${jobId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        setSavedJobs(prev => {
          const newSet = new Set(prev)
          newSet.delete(jobId)
          return newSet
        })
      }
    } catch (err) {
      console.error('Error unsaving job:', err)
    }
  }

  const applyFilters = () => {
    let filtered = [...jobs]

    if (filters.minScore > 0) {
      filtered = filtered.filter(match => match.compatibility_score >= filters.minScore)
    }

    if (filters.location) {
      filtered = filtered.filter(match => 
        match.job.location.toLowerCase().includes(filters.location.toLowerCase())
      )
    }

    if (filters.salaryMin > 0 || filters.salaryMax < 10000000) {
      filtered = filtered.filter(match => {
        const jobMin = match.job.salary_min || 0
        const jobMax = match.job.salary_max || 0
        return jobMax >= filters.salaryMin && jobMin <= filters.salaryMax
      })
    }

    if (filters.companyType) {
      filtered = filtered.filter(match => match.job.company_type === filters.companyType)
    }

    if (filters.remoteOption) {
      filtered = filtered.filter(match => match.job.remote_option === filters.remoteOption)
    }

    filtered.sort((a, b) => {
      switch (filters.sortBy) {
        case 'compatibility':
          return b.compatibility_score - a.compatibility_score
        case 'salary':
          return (b.job.salary_max || 0) - (a.job.salary_max || 0)
        case 'companyFit':
          return (b.company_fit_score || 0) - (a.company_fit_score || 0)
        default:
          return 0
      }
    })

    setFilteredJobs(filtered)
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
          fetchResumeAnalysis()
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
      {/* Header */}
      <div className="mb-8 flex flex-col md:flex-row md:justify-between md:items-center gap-4 bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Job Recommendations
          </h1>
          <p className="text-gray-600 mt-2 text-lg">✨ AI-powered matches tailored for you</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="bg-white border-2 border-blue-600 text-blue-600 px-6 py-3 rounded-xl hover:bg-blue-50 transition-all inline-flex items-center space-x-2 font-semibold"
          >
            <span>🔍</span>
            <span>Filters</span>
          </button>
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
      </div>

      {/* Resume Analysis Card */}
      {resumeAnalysis && (
        <ResumeAnalysisCard analysis={resumeAnalysis} isPremium={user?.is_premium} />
      )}

      {/* Success/Error Messages */}
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

      {/* Filter Panel */}
      {showFilters && (
        <FilterPanel filters={filters} setFilters={setFilters} />
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4 border border-blue-200">
          <div className="text-3xl font-bold text-blue-600">{filteredJobs.length}</div>
          <div className="text-sm text-blue-700">Matching Jobs</div>
        </div>
        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-4 border border-green-200">
          <div className="text-3xl font-bold text-green-600">{savedJobs.size}</div>
          <div className="text-sm text-green-700">Saved Jobs</div>
        </div>
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-4 border border-purple-200">
          <div className="text-3xl font-bold text-purple-600">
            {filteredJobs.length > 0 ? Math.round(filteredJobs[0].compatibility_score) : 0}%
          </div>
          <div className="text-sm text-purple-700">Top Match Score</div>
        </div>
      </div>

      {/* Job List */}
      {loading ? (
        <div className="grid gap-6">
          <JobCardSkeleton />
          <JobCardSkeleton />
          <JobCardSkeleton />
        </div>
      ) : filteredJobs.length === 0 ? (
        <div className="bg-gradient-to-br from-gray-50 to-blue-50 rounded-2xl shadow-xl p-16 text-center border-2 border-gray-200">
          <div className="text-8xl mb-6 animate-bounce">🔍</div>
          <h3 className="text-2xl font-bold text-gray-900 mb-3">No Matches Found</h3>
          <p className="text-gray-600 text-lg max-w-md mx-auto">
            Try adjusting your filters or updating your resume for better matches.
          </p>
        </div>
      ) : (
        <div className="grid gap-6">
          {filteredJobs.map((match, index) => (
            <JobCard
              key={match.job.id}
              match={match}
              index={index}
              isSaved={savedJobs.has(match.job.id)}
              onSave={() => handleSaveJob(match.job.id)}
              onUnsave={() => handleUnsaveJob(match.job.id)}
              isPremium={user?.is_premium}
              onClick={() => navigate(`/jobs/${match.job.id}`)}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default Dashboard
