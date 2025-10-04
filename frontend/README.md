# Customer Retention Agent Frontend

A Next.js frontend application for the Customer Retention Agent with real Cognito authentication.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ installed
- AWS credentials configured (for Cognito authentication)
- Cognito User Pool with test user created

### Installation

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Set up environment variables:**
   ```bash
   cp env.example .env.local
   ```
   
   Update `.env.local` with your actual values:
   ```env
   NEXT_PUBLIC_AWS_REGION=us-east-1
   NEXT_PUBLIC_USER_POOL_ID=YOUR_USER_POOL_ID
   NEXT_PUBLIC_USER_POOL_WEB_CLIENT_ID=YOUR_CLIENT_ID
   NEXT_PUBLIC_USER_POOL_WEB_CLIENT_SECRET=YOUR_CLIENT_SECRET
   AGENTCORE_RUNTIME_ARN=arn:aws:bedrock-agentcore:us-east-1:YOUR_ACCOUNT_ID:runtime/main-7rUSst3r7E
   AGENTCORE_RUNTIME_ID=main-7rUSst3r7E
   ```
   
   **⚠️ Important**: You need to get the client secret from AWS Cognito Console:
   1. Go to AWS Cognito Console
   2. Select your User Pool
   3. Go to "App clients" tab
   4. Click on your Web Client
   5. Click "Show client secret"
   6. Copy the secret and add it to your `.env.local` file

3. **Run the development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   Navigate to [http://localhost:3000](http://localhost:3000)

## 🔐 Authentication

The frontend now uses **real Cognito authentication**:

- **Sign in** with your Cognito User Pool credentials
- **Test user**: `testuser` (if configured in your User Pool)
- **JWT tokens** are automatically managed and stored
- **Logout** clears all authentication tokens

### Test User Setup

If you haven't created a test user in your Cognito User Pool:

1. Go to AWS Cognito Console
2. Select your User Pool
3. Go to "Users" tab
4. Click "Create user"
5. Set username: `testuser`
6. Set password: `TestPassword123!`
7. Uncheck "Mark email as verified" (for demo purposes)

**⚠️ Important**: Make sure your Cognito Web Client has `USER_PASSWORD_AUTH` flow enabled for the frontend authentication to work.

## 🏗️ Architecture

- **Authentication**: AWS Cognito with JWT tokens
- **API Integration**: Direct calls to AgentCore Runtime
- **State Management**: React hooks for local state
- **Styling**: Tailwind CSS
- **Customer Mapping**: JWT user ID to customer ID mapping for personalized experiences

## 🔧 Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_AWS_REGION` | AWS region | `us-east-1` |
| `NEXT_PUBLIC_USER_POOL_ID` | Cognito User Pool ID | `YOUR_USER_POOL_ID` |
| `NEXT_PUBLIC_USER_POOL_WEB_CLIENT_ID` | Cognito Web Client ID | `YOUR_CLIENT_ID` |
| `NEXT_PUBLIC_USER_POOL_WEB_CLIENT_SECRET` | Cognito Web Client Secret | `YOUR_CLIENT_SECRET` |
| `AGENTCORE_RUNTIME_ARN` | AgentCore Runtime ARN | `arn:aws:bedrock-agentcore:us-east-1:YOUR_ACCOUNT_ID:runtime/main-7rUSst3r7E` |
| `AGENTCORE_RUNTIME_ID` | AgentCore Runtime ID | `main-7rUSst3r7E` |

### Cognito Configuration

The frontend is configured to work with:
- **User Pool**: Your Cognito User Pool
- **Web Client**: Your Cognito Web Client
- **Authentication Flow**: `USER_PASSWORD_AUTH` (must be enabled)
- **JWT Authentication**: For AgentCore Runtime integration

## 🚀 Deployment

### Vercel Deployment

1. **Connect to Vercel:**
   ```bash
   npm install -g vercel
   vercel
   ```

2. **Set environment variables in Vercel dashboard:**
   - `NEXT_PUBLIC_AWS_REGION`
   - `NEXT_PUBLIC_USER_POOL_ID`
   - `NEXT_PUBLIC_USER_POOL_WEB_CLIENT_ID`
   - `NEXT_PUBLIC_USER_POOL_WEB_CLIENT_SECRET`
   - `AGENTCORE_RUNTIME_ARN`
   - `AGENTCORE_RUNTIME_ID`

3. **Deploy:**
   ```bash
   vercel --prod
   ```

## 🐛 Troubleshooting

### Common Issues

1. **"Authentication failed"**
   - Check if test user exists in Cognito User Pool
   - Verify username/password are correct
   - Check browser console for detailed error messages

2. **"No valid authentication token found"**
   - Clear browser localStorage
   - Sign in again
   - Check if JWT token is expired

3. **CORS errors**
   - Ensure Cognito User Pool allows your domain
   - Check if Web Client is configured correctly

4. **"USER_PASSWORD_AUTH flow not enabled"**
   - Go to Cognito Console → User Pool → App clients
   - Select your Web Client
   - Enable "USER_PASSWORD_AUTH" authentication flow

5. **AgentCore Runtime connection issues**
   - Verify `AGENTCORE_RUNTIME_ARN` is correct
   - Check if the runtime is deployed and running
   - Ensure JWT tokens are being sent correctly

### Debug Mode

Enable debug logging by opening browser console and looking for:
- Authentication attempts
- Token storage/retrieval
- API call details

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── api/chat/route.ts    # API route for AgentCore Runtime
│   │   ├── layout.tsx           # Root layout
│   │   └── page.tsx             # Main page with auth logic
│   ├── components/
│   │   ├── ChatInterface.tsx    # Chat UI component
│   │   ├── LoginForm.tsx        # Authentication form
│   │   ├── MessageBubble.tsx    # Message display
│   │   ├── MessageInput.tsx     # Message input
│   │   └── TypingIndicator.tsx  # Loading indicator
│   └── lib/
│       └── cognito-auth.ts      # Cognito authentication utilities
├── env.example                  # Environment variables template
└── README.md                    # This file
```

## 🔗 Related Documentation

- [AWS Cognito Documentation](https://docs.aws.amazon.com/cognito/)
- [Next.js Documentation](https://nextjs.org/docs)
- [AgentCore Runtime Documentation](https://docs.aws.amazon.com/bedrock-agentcore/)