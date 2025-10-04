'use client'

import { useState } from 'react'
import { ChatInterface } from '@/components/ChatInterface'
import { LoginForm } from '@/components/LoginForm'
import { clearAuthTokens } from '@/lib/cognito-auth'

export default function HomePage() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [user, setUser] = useState<{ username: string; customerId: string } | null>(null)

  const handleLogin = (username: string) => {
    setUser({ username, customerId: username })
    setIsLoggedIn(true)
  }

  const handleLogout = () => {
    // Clear Cognito authentication tokens
    if (user?.username) {
      clearAuthTokens(user.username)
    }
    
    setUser(null)
    setIsLoggedIn(false)
  }

  if (!isLoggedIn) {
    return <LoginForm onLogin={handleLogin} />
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-semibold text-gray-900">
              Customer Retention Agent
            </h1>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">Welcome, {user?.username}</span>
              <button
                onClick={handleLogout}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </header>
      
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <ChatInterface customerId={user?.customerId || 'unknown'} />
        </div>
      </main>
    </div>
  )
}