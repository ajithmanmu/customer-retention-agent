'use client'

import { User, Bot } from 'lucide-react'

// Simple text formatter - just clean up the text and make it readable
function FormattedMessage({ content }: { content: string }) {
  // Just convert \n to actual newlines and display as plain text
  const cleanContent = content.replace(/\\n/g, '\n')
  
  return (
    <div className="whitespace-pre-wrap text-sm leading-relaxed">
      {cleanContent}
    </div>
  )
}

interface Message {
  id: string
  content: string
  role: 'user' | 'agent'
  timestamp: Date
}

interface MessageBubbleProps {
  message: Message
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user'
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex items-start space-x-2 max-w-sm lg:max-w-2xl ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser ? 'bg-blue-600' : 'bg-gray-200'
        }`}>
          {isUser ? (
            <User className="w-4 h-4 text-white" />
          ) : (
            <Bot className="w-4 h-4 text-gray-600" />
          )}
        </div>
        
        {/* Message Content */}
        <div className={`max-w-sm lg:max-w-2xl px-4 py-2 rounded-lg ${
          isUser 
            ? 'bg-blue-600 text-white ml-auto' 
            : 'bg-gray-100 text-gray-900 mr-auto'
        }`}>
          <div className="text-sm">
            {isUser ? (
              <p className="whitespace-pre-wrap">{message.content}</p>
            ) : (
              <FormattedMessage content={message.content} />
            )}
          </div>
          <p className={`text-xs mt-1 ${
            isUser ? 'text-blue-100' : 'text-gray-500'
          }`}>
            {message.timestamp.toLocaleTimeString([], { 
              hour: '2-digit', 
              minute: '2-digit' 
            })}
          </p>
        </div>
      </div>
    </div>
  )
}