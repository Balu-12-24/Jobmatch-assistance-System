import React from 'react'

const FilterPanel = ({ filters, setFilters }) => {
  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }

  const resetFilters = () => {
    setFilters({
      minScore: 0,
      location: '',
      salaryMin: 0,
      salaryMax: 10000000,
      companyType: '',
      remoteOption: '',
      sortBy: 'compatibility'
    })
  }

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 mb-6 border border-gray-200 animate-slideIn">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-bold text-gray-900">🔍 Filters & Sorting</h3>
        <button
          onClick={resetFilters}
          className="text-sm text-blue-600 hover:text-blue-800 font-semibold"
        >
          Reset All
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Minimum Match Score */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Minimum Match Score: {filters.minScore}%
          </label>
          <input
            type="range"
            min="0"
            max="100"
            value={filters.minScore}
            onChange={(e) => handleFilterChange('minScore', parseInt(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          />
        </div>

        {/* Location */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Location
          </label>
          <input
            type="text"
            placeholder="e.g., Bangalore, Mumbai"
            value={filters.location}
            onChange={(e) => handleFilterChange('location', e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Salary Range */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Salary Range (₹)
          </label>
          <div className="flex gap-2">
            <input
              type="number"
              placeholder="Min"
              value={filters.salaryMin}
              onChange={(e) => handleFilterChange('salaryMin', parseInt(e.target.value) || 0)}
              className="w-1/2 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <input
              type="number"
              placeholder="Max"
              value={filters.salaryMax === 10000000 ? '' : filters.salaryMax}
              onChange={(e) => handleFilterChange('salaryMax', parseInt(e.target.value) || 10000000)}
              className="w-1/2 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Company Type */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Company Type
          </label>
          <select
            value={filters.companyType}
            onChange={(e) => handleFilterChange('companyType', e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Types</option>
            <option value="MNC">MNC</option>
            <option value="startup">Startup</option>
            <option value="service">Service</option>
            <option value="product">Product</option>
            <option value="BPO">BPO</option>
            <option value="KPO">KPO</option>
          </select>
        </div>

        {/* Remote Option */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Work Mode
          </label>
          <select
            value={filters.remoteOption}
            onChange={(e) => handleFilterChange('remoteOption', e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Modes</option>
            <option value="remote">Remote</option>
            <option value="hybrid">Hybrid</option>
            <option value="onsite">Onsite</option>
          </select>
        </div>

        {/* Sort By */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Sort By
          </label>
          <select
            value={filters.sortBy}
            onChange={(e) => handleFilterChange('sortBy', e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="compatibility">Match Score</option>
            <option value="salary">Salary (High to Low)</option>
            <option value="companyFit">Company Fit</option>
          </select>
        </div>
      </div>
    </div>
  )
}

export default FilterPanel
