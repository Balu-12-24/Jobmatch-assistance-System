import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const JobDetail = () => {
  const { id } = useParams()
  const [job, setJob] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const { token, user } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    fetchJobDetails()
  }, [id])

  const fetchJobDetails = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/jobs/${id}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data = await response.json()
      setJob(data)
    } catch (err) {
      console.error('Error fetching job:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSaveJob = async () => {
    setSaving(true)
    try {
      await fetch(`http://localhost:8000/api/jobs/save?job_id=${id}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      alert('Job saved successfully!')
    } catch (err) {
      alert('Error saving job')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return <div className="text-center py-12">Loading...</div>
  }

  if (!job) {
    return <div className="text-center py-12">Job not found</div>
  }

  return (
    <div className="max-w-4xl mx-auto">
      <button
        onClick={() => navigate('/dashboard')}
        className="text-blue-600 hover:text-blue-700 mb-6 flex items-center"
      >
        ← Back to Dashboard
      </button>

      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{job.title}</h1>
            <p className="text-xl text-gray-700">{job.company}</p>
            <p className="text-gray-600 mt-2">
              {job.location} • {job.remote_option} • {job.job_type}
            </p>
          </div>
          <button
            onClick={handleSaveJob}
            disabled={saving}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save Job'}
          </button>
        </div>

        {job.salary_min && job.salary_max && (
          <div className="mb-6 p-4 bg-green-50 rounded-lg">
            <p className="text-lg font-semibold text-gray-900">
              Salary Range: ${job.salary_min.toLocaleString()} - ${job.salary_max.toLocaleString()}
            </p>
          </div>
        )}

        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-3">Description</h2>
          <p className="text-gray-700 whitespace-pre-line">{job.description}</p>
        </div>

        {job.requirements && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-3">Requirements</h2>
            <p className="text-gray-700 whitespace-pre-line">{job.requirements}</p>
          </div>
        )}

        <div className="grid grid-cols-2 gap-4 pt-6 border-t">
          {job.company_size && (
            <div>
              <p className="text-sm text-gray-600">Company Size</p>
              <p className="font-semibold text-gray-900 capitalize">{job.company_size}</p>
            </div>
          )}
          {job.industry && (
            <div>
              <p className="text-sm text-gray-600">Industry</p>
              <p className="font-semibold text-gray-900 capitalize">{job.industry}</p>
            </div>
          )}
        </div>

        {!user.is_premium && (
          <div className="mt-8 p-6 bg-yellow-50 border border-yellow-200 rounded-lg">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Upgrade to Premium
            </h3>
            <p className="text-gray-700 mb-4">
              Get detailed salary predictions, company-fit insights, and skill gap analysis
            </p>
            <button
              onClick={() => navigate('/profile')}
              className="bg-yellow-500 text-white px-6 py-2 rounded-lg hover:bg-yellow-600"
            >
              Upgrade Now
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default JobDetail
