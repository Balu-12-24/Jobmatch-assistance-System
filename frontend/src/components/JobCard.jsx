import React from 'react'

const JobCard = ({ match, index, isSaved, onSave, onUnsave, isPremium, onClick }) => {
  const { job, compatibility_score, matching_skills, missing_skills, salary_prediction, company_fit_score } = match

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-gray-600'
  }

  const formatSalary = (min, max, currency = 'INR') => {
    if (currency === 'INR') {
      const minLPA = (min / 100000).toFixed(1)
      const maxLPA = (max / 100000).toFixed(1)
      return `₹${minLPA} - ${maxLPA} LPA`
    }
    return `$${min.toLocaleString()} - $${max.toLocaleString()}`
  }

  const getCityTierBadge = (tier) => {
    const badges = {
      1: { text: 'Tier 1', color: 'bg-blue-100 text-blue-800' },
      2: { text: 'Tier 2', color: 'bg-green-100 text-green-800' },
      3: { text: 'Tier 3', color: 'bg-gray-100 text-gray-800' }
    }
    return badges[tier] || badges[1]
  }

  const getCompanyTypeBadge = (type) => {
    const badges = {
      'MNC': { icon: '🏢', color: 'bg-purple-100 text-purple-800' },
      'startup': { icon: '🚀', color: 'bg-pink-100 text-pink-800' },
      'service': { icon: '⚙️', color: 'bg-blue-100 text-blue-800' },
      'product': { icon: '📦', color: 'bg-green-100 text-green-800' },
      'BPO': { icon: '📞', color: 'bg-yellow-100 text-yellow-800' },
      'KPO': { icon: '🧠', color: 'bg-indigo-100 text-indigo-800' }
    }
    return badges[type] || { icon: '🏢', color: 'bg-gray-100 text-gray-800' }
  }

  const handleSaveClick = (e) => {
    e.stopPropagation()
    if (isSaved) {
      onUnsave()
    } else {
      onSave()
    }
  }

  const cityTier = getCityTierBadge(job.city_tier)
  const companyType = getCompanyTypeBadge(job.company_type)

  return (
    <div
      className="bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 p-6 cursor-pointer border-2 border-transparent hover:border-blue-300 transform hover:-translate-y-2 animate-fadeIn relative"
      style={{ animationDelay: `${index * 100}ms` }}
      onClick={onClick}
    >
      {/* Save Button */}
      <button
        onClick={handleSaveClick}
        className="absolute top-4 right-4 text-2xl hover:scale-110 transition-transform"
      >
        {isSaved ? '❤️' : '🤍'}
      </button>

      {/* Header */}
      <div className="flex justify-between items-start mb-4 pr-8">
        <div className="flex-1">
          <h3 className="text-2xl font-bold text-gray-900 mb-1">{job.title}</h3>
          <p className="text-lg text-gray-700 font-semibold">{job.company}</p>
          
          {/* Location and Details */}
          <div className="flex flex-wrap items-center gap-2 mt-3">
            <span className="flex items-center text-sm text-gray-600 bg-gray-100 px-3 py-1 rounded-full">
              <span className="mr-1">📍</span>
              {job.location}
            </span>
            {job.city_tier && (
              <span className={`text-xs px-2 py-1 rounded-full font-semibold ${cityTier.color}`}>
                {cityTier.text}
              </span>
            )}
            <span className="flex items-center text-sm text-gray-600 bg-gray-100 px-3 py-1 rounded-full">
              <span className="mr-1">💼</span>
              {job.remote_option}
            </span>
            {job.company_type && (
              <span className={`text-xs px-2 py-1 rounded-full font-semibold ${companyType.color}`}>
                {companyType.icon} {job.company_type}
              </span>
            )}
          </div>
        </div>
        
        {/* Match Score */}
        <div className="text-right ml-4">
          <div className={`text-4xl font-bold ${getScoreColor(compatibility_score)} mb-1`}>
            {Math.round(compatibility_score)}%
          </div>
          <p className="text-sm text-gray-500 font-semibold">Match</p>
        </div>
      </div>

      {/* Salary */}
      {(job.salary_min && job.salary_max) || salary_prediction ? (
        <div className="mb-4">
          <div className="bg-green-50 border border-green-200 rounded-lg px-4 py-3 inline-block">
            <p className="text-green-800 font-semibold flex items-center">
              <span className="mr-2">💰</span>
              {salary_prediction ? (
                <>
                  {formatSalary(salary_prediction.predicted_min, salary_prediction.predicted_max, job.salary_currency)}
                  {isPremium && salary_prediction.confidence && (
                    <span className="ml-2 text-xs text-green-600">
                      ({Math.round(salary_prediction.confidence * 100)}% confidence)
                    </span>
                  )}
                </>
              ) : (
                formatSalary(job.salary_min, job.salary_max, job.salary_currency)
              )}
            </p>
          </div>
          {!isPremium && salary_prediction && (
            <span className="ml-2 text-xs text-purple-600 font-semibold">
              👑 Premium: Detailed breakdown available
            </span>
          )}
        </div>
      ) : null}

      {/* Matching Skills */}
      {matching_skills && matching_skills.length > 0 && (
        <div className="mb-4">
          <p className="text-sm text-gray-600 mb-2 font-semibold">✅ Matching Skills:</p>
          <div className="flex flex-wrap gap-2">
            {matching_skills.slice(0, 6).map((skill, idx) => (
              <span key={idx} className="bg-gradient-to-r from-green-100 to-green-200 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                {skill}
              </span>
            ))}
            {matching_skills.length > 6 && (
              <span className="text-gray-500 text-sm self-center">+{matching_skills.length - 6} more</span>
            )}
          </div>
        </div>
      )}

      {/* Missing Skills (Skill Gap) */}
      {missing_skills && missing_skills.length > 0 && (
        <div className="mb-4">
          <p className="text-sm text-gray-600 mb-2 font-semibold">📚 Skills to Learn:</p>
          <div className="flex flex-wrap gap-2">
            {missing_skills.slice(0, 4).map((skill, idx) => (
              <span key={idx} className="bg-gradient-to-r from-orange-100 to-orange-200 text-orange-800 px-3 py-1 rounded-full text-sm font-medium">
                {skill}
              </span>
            ))}
            {missing_skills.length > 4 && (
              <span className="text-gray-500 text-sm self-center">+{missing_skills.length - 4} more</span>
            )}
          </div>
        </div>
      )}

      {/* Company Fit Score */}
      {company_fit_score && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span>🏢</span>
              <span className="text-sm text-gray-600">Company Fit:</span>
              <span className="font-bold text-purple-600">{Math.round(company_fit_score)}%</span>
            </div>
            {!isPremium && (
              <span className="text-xs text-purple-600 font-semibold">
                👑 Premium: Detailed insights
              </span>
            )}
          </div>
        </div>
      )}

      {/* View Details */}
      <div className="mt-4 pt-4 border-t border-gray-200 flex justify-between items-center">
        <span className="text-blue-600 text-sm font-semibold">View Full Details →</span>
        <div className="flex gap-2">
          {job.job_type && (
            <span className="text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded">
              {job.job_type}
            </span>
          )}
          {job.industry && (
            <span className="text-xs bg-purple-50 text-purple-700 px-2 py-1 rounded">
              {job.industry}
            </span>
          )}
        </div>
      </div>
    </div>
  )
}

export default JobCard
