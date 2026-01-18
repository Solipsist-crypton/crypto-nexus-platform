import React from 'react'

const Footer: React.FC = () => {
  return (
    <footer className="mt-8 p-4 border-t border-gray-200 dark:border-gray-800 text-center text-gray-600 dark:text-gray-400">
      <p>Crypto Nexus Platform © {new Date().getFullYear()}</p>
      <p className="text-sm mt-1">All rights reserved</p>
    </footer>
  )
}

export default Footer