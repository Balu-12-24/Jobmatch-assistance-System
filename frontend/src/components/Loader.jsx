import React from 'react'

// Unique animated loader component with gradient orbs
export const Loader = ({ size = 'md', text = '' }) => {
  const sizes = {
    sm: { container: 'w-12 h-12', orb: 'w-3 h-3' },
    md: { container: 'w-20 h-20', orb: 'w-5 h-5' },
    lg: { container: 'w-32 h-32', orb: 'w-7 h-7' }
  }

  return (
    <div className="flex flex-col items-center justify-center py-8">
      <div className={`relative ${sizes[size].container}`}>
        {/* Rotating gradient orbs */}
        <div className="absolute inset-0 animate-spin" style={{ animationDuration: '2s' }}>
          <div className={`absolute top-0 left-1/2 -translate-x-1/2 ${sizes[size].orb} bg-gradient-to-br from-blue-500 to-blue-600 rounded-full shadow-lg`}></div>
        </div>
        <div className="absolute inset-0 animate-spin" style={{ animationDuration: '2s', animationDelay: '0.33s' }}>
          <div className={`absolute top-0 left-1/2 -translate-x-1/2 ${sizes[size].orb} bg-gradient-to-br from-purple-500 to-purple-600 rounded-full shadow-lg`}></div>
        </div>
        <div className="absolute inset-0 animate-spin" style={{ animationDuration: '2s', animationDelay: '0.66s' }}>
          <div className={`absolute top-0 left-1/2 -translate-x-1/2 ${sizes[size].orb} bg-gradient-to-br from-pink-500 to-pink-600 rounded-full shadow-lg`}></div>
        </div>
        {/* Center glow */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-2 h-2 bg-white rounded-full animate-pulse shadow-xl"></div>
        </div>
      </div>
      {text && (
        <p className="mt-6 text-gray-700 font-medium animate-pulse text-center">{text}</p>
      )}
    </div>
  )
}

// Skeleton loader for job cards with gradient shimmer
export const JobCardSkeleton = () => {
  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 border-2 border-gray-100 overflow-hidden relative">
      {/* Shimmer effect */}
      <div className="absolute inset-0 -translate-x-full animate-[shimmer_2s_infinite] bg-gradient-to-r from-transparent via-white to-transparent opacity-50"></div>
      
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <div className="h-8 bg-gradient-to-r from-gray-200 to-gray-300 rounded-lg w-3/4 mb-3"></div>
          <div className="h-6 bg-gradient-to-r from-gray-200 to-gray-300 rounded-lg w-1/2 mb-3"></div>
          <div className="flex gap-3">
            <div className="h-5 bg-gradient-to-r from-gray-200 to-gray-300 rounded-lg w-24"></div>
            <div className="h-5 bg-gradient-to-r from-gray-200 to-gray-300 rounded-lg w-24"></div>
          </div>
        </div>
        <div className="ml-4">
          <div className="h-16 w-20 bg-gradient-to-br from-gray-200 to-gray-300 rounded-xl"></div>
        </div>
      </div>
      
      <div className="h-10 bg-gradient-to-r from-green-100 to-green-200 rounded-lg w-48 mb-4"></div>
      
      <div className="mb-4">
        <div className="h-4 bg-gradient-to-r from-gray-200 to-gray-300 rounded w-32 mb-2"></div>
        <div className="flex flex-wrap gap-2">
          <div className="h-8 w-20 bg-gradient-to-r from-blue-100 to-blue-200 rounded-full"></div>
          <div className="h-8 w-24 bg-gradient-to-r from-blue-100 to-blue-200 rounded-full"></div>
          <div className="h-8 w-20 bg-gradient-to-r from-blue-100 to-blue-200 rounded-full"></div>
          <div className="h-8 w-28 bg-gradient-to-r from-blue-100 to-blue-200 rounded-full"></div>
        </div>
      </div>
      
      <div className="pt-4 border-t border-gray-200 flex justify-between items-center">
        <div className="h-5 bg-gradient-to-r from-purple-100 to-purple-200 rounded w-32"></div>
        <div className="h-5 bg-gradient-to-r from-gray-200 to-gray-300 rounded w-24"></div>
      </div>
    </div>
  )
}

// Pulsing dots loader
export const DotsLoader = () => {
  return (
    <div className="flex space-x-2">
      <div className="w-3 h-3 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
      <div className="w-3 h-3 bg-purple-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
      <div className="w-3 h-3 bg-pink-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
    </div>
  )
}

export default Loader
