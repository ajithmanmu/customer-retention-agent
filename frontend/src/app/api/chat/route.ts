import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { prompt, customerId, jwtToken } = body

    if (!prompt) {
      return NextResponse.json(
        { error: 'Prompt is required' },
        { status: 400 }
      )
    }

    if (!jwtToken) {
      return NextResponse.json(
        { error: 'JWT token is required' },
        { status: 400 }
      )
    }

    // Generate a unique session ID (33+ characters as required)
    const timestamp = Date.now().toString()
    const random1 = Math.random().toString(36).substring(2, 15)
    const random2 = Math.random().toString(36).substring(2, 15)
    const random3 = Math.random().toString(36).substring(2, 10)
    const runtimeSessionId = `session-${timestamp}-${random1}-${random2}-${random3}`
    
    // Debug: Log the session ID length
    console.log(`Generated runtimeSessionId: ${runtimeSessionId} (length: ${runtimeSessionId.length})`)

    const agentRuntimeArn = process.env.AGENTCORE_RUNTIME_ARN || 'arn:aws:bedrock-agentcore:us-east-1:YOUR_ACCOUNT_ID:runtime/main-7rUSst3r7E'
    const escapedArn = encodeURIComponent(agentRuntimeArn)
    const endpointUrl = `https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/${escapedArn}/invocations`

    const response = await fetch(endpointUrl, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${jwtToken}`,
        'Content-Type': 'application/json',
        'X-Amzn-Bedrock-AgentCore-Runtime-Session-Id': runtimeSessionId,
      },
      body: JSON.stringify({
        prompt: prompt.trim(),
        customerId: customerId,
      }),
    })

    if (!response.ok) {
      throw new Error(`AgentCore Runtime request failed: ${response.status} ${response.statusText}`)
    }

    const textResponse = await response.text()
    let agentMessage = textResponse

    // Try to parse as JSON if it looks like JSON
    try {
      const parsedResponse = JSON.parse(textResponse)
      agentMessage = parsedResponse.message || parsedResponse.response || textResponse
    } catch {
      // If not JSON, use the text as is
      agentMessage = textResponse
    }

    return NextResponse.json({
      message: agentMessage,
      customerId: customerId,
      sessionId: runtimeSessionId,
      timestamp: new Date().toISOString(),
    })

  } catch (error) {
    console.error('Error in chat API:', error)
    return NextResponse.json(
      { 
        error: 'Failed to process chat request',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}