import React, { useState } from 'react'

const ResumeAnalysisCard = ({ analysis, isPremium }) => {
  const [expanded, setExpanded] = useState(false)

  if (!analysis) return null

  const { ats_score, strong_sections, weak_sections, improvement_suggestions } = analysis

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getScoreBg = (score) => {
    if (score >= 80) return 'bg-green-50 border-green-200'
    if (score >= 60) return 'bg-yellow-50 border-yellow-200'
    return 'bg-red-50 border-red-200'
  }

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 mb-6 border-2 border-blue-100">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">📊 Resume Analysis</h2>
          <p className="text-gray-600">ATS Compatibility Score</p>
        </div>
        <div className="text-right">
          <div className={`text-5xl font-bold ${getScoreColor(ats_score.overall_score)}`}>
            {ats_score.overall_score}
          </div>
          <p className="text-sm text-gray-500 font-semibold">/ 100</p>
        </div>
      </div>

      {/* Score Breakdown */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
        <div className={`${getScoreBg(ats_score.formatting_score)} rounded-lg p-3 border-2`}>
          <div className={`text-2xl font-bold ${getScoreColor(ats_score.formatting_score)}`}>
            {ats_score.formatting_score}
          </div>
          <div className="text-xs text-gray-600">Formatting</div>
        </div>
        <div className={`${getScoreBg(ats_score.keywords_score)} rounded-lg p-3 border-2`}>
          <div className={`text-2xl font-bold ${getScoreColor(ats_score.keywords_score)}`}>
            {ats_score.keywords_score}
          </div>
          <div className="text-xs text-gray-600">Keywords</div>
        </div>
        <div className={`${getScoreBg(ats_score.experience_score)} rounded-lg p-3 border-2`}>
          <div className={`text-2xl font-bold ${getScoreColor(ats_score.experience_score)}`}>
            {ats_score.experience_score}
          </div>
          <div className="text-xs text-gray-600">Experience</div>
        </div>
        <div className={`${getScoreBg(ats_score.education_score)} rounded-lg p-3 border-2`}>
          <div className={`text-2xl font-bold ${getScoreColor(ats_score.education_score)}`}>
            {ats_score.education_score}
          </div>
          <div className="text-xs text-gray-600">Education</div>
        </div>
        <div className={`${getScoreBg(ats_score.readability_score)} rounded-lg p-3 border-2`}>
          <div className={`text-2xl font-bold ${getScoreColor(ats_score.readability_score)}`}>
            {ats_score.readability_score}
          </div>
          <div className="text-xs text-gray-600">Readability</div>
        </div>
      </div>

      {/* Quick Summary */}
      <div className="grid md:grid-cols-2 gap-4 mb-4">
        {strong_sections && strong_sections.length > 0 && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h3 className="font-bold text-green-800 mb-2 flex items-center">
              <span className="mr-2">✅</span>
              Strong Sections ({strong_sections.length})
            </h3>
            <ul className="text-sm text-green-700 space-y-1">
              {strong_sections.slice(0, 3).map((section, idx) => (
                <li key={idx}>• {section.section}</li>
              ))}
            </ul>
          </div>
        )}

        {weak_sections && weak_sections.length > 0 && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <h3 className="font-bold text-yellow-800 mb-2 flex items-center">
              <span className="mr-2">⚠️</span>
              Needs Improvement ({weak_sections.length})
            </h3>
            <ul className="text-sm text-yellow-700 space-y-1">
              {weak_sections.slice(0, 3).map((section, idx) => (
                <li key={idx}>• {section.section}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Expand/Collapse Button */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full bg-blue-50 hover:bg-blue-100 text-blue-600 font-semibold py-2 px-4 rounded-lg transition-colors"
      >
        {expanded ? '▲ Show Less' : '▼ Show Detailed Analysis'}
      </button>

      {/* Detailed Analysis */}
      {expanded && (
        <div className="mt-6 space-y-6 animate-fadeIn">
          {/* Improvement Suggestions */}
          {improvement_suggestions && improvement_suggestions.length > 0 && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-bold text-blue-800 mb-3 flex items-center">
                <span className="mr-2">💡</span>
                Improvement Suggestions
              </h3>
              <ul className="text-sm text-blue-700 space-y-2">
                {improvement_suggestions.map((suggestion, idx) => (
                  <li key={idx} className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>{suggestion}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Strong Sections Detail */}
          {strong_sections && strong_sections.length > 0 && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h3 className="font-bold text-green-800 mb-3">✅ Strong Sections (Detailed)</h3>
              <div className="space-y-3">
                {strong_sections.map((section, idx) => (
                  <div key={idx} className="bg-white rounded p-3">
                    <div className="font-semibold text-green-800">{section.section}</div>
                    <div className="text-sm text-green-700 mt-1">{section.reason}</div>
                    {section.examples && section.examples.length > 0 && (
                      <div className="text-xs text-gray-600 mt-2">
                        Examples: {section.examples.join(', ')}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Weak Sections Detail */}
          {weak_sections && weak_sections.length > 0 && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <h3 className="font-bold text-yellow-800 mb-3">⚠️ Areas for Improvement</h3>
              <div className="space-y-3">
                {weak_sections.map((section, idx) => (
                  <div key={idx} className="bg-white rounded p-3">
                    <div className="font-semibold text-yellow-800">{section.section}</div>
                    <div className="text-sm text-yellow-700 mt-1">{section.issue}</div>
                    {section.suggestions && section.suggestions.length > 0 && (
                      <div className="text-xs text-gray-600 mt-2">
                        <strong>Suggestions:</strong>
                        <ul className="ml-4 mt-1">
                          {section.suggestions.map((sug, i) => (
                            <li key={i}>• {sug}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Premium Features Teaser */}
          {!isPremium && (
            <div className="bg-gradient-to-r from-purple-50 to-pink-50 border-2 border-purple-200 rounded-lg p-6 text-center">
              <div className="text-4xl mb-3">👑</div>
              <h3 className="font-bold text-purple-800 mb-2">Unlock Premium Analysis</h3>
              <p className="text-sm text-purple-700 mb-4">
                Get line-by-line suggestions, industry-specific keywords, and detailed keyword gap analysis
              </p>
              <button className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-2 rounded-lg font-semibold hover:shadow-lg transition-all">
                Upgrade to Premium
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default ResumeAnalysisCard
