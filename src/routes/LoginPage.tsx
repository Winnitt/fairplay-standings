import { useState, type FormEvent } from 'react'
import { Navigate } from 'react-router'
import { useAuthContext } from '@/lib/AuthProvider'
import { useRequestOtp, useVerifyOtp } from '@/hooks/useOtp'
import { Footer } from '@/components/Footer'

export function LoginPage() {
  const { session, loading } = useAuthContext()
  const [email, setEmail] = useState('')
  const [token, setToken] = useState('')
  const [sent, setSent] = useState(false)

  const requestOtp = useRequestOtp()
  const verifyOtp = useVerifyOtp()

  if (loading) return <p className="state">Loading…</p>
  if (session) return <Navigate to="/admin/men" replace />

  function handleSendCode(event: FormEvent) {
    event.preventDefault()
    requestOtp.mutate(email.trim(), { onSuccess: () => setSent(true) })
  }

  function handleVerify(event: FormEvent) {
    event.preventDefault()
    verifyOtp.mutate({ email: email.trim(), token: token.trim() })
  }

  const error = requestOtp.error ?? verifyOtp.error

  return (
    <>
      <main className="page page--centered">
        <form className="card login" onSubmit={sent ? handleVerify : handleSendCode}>
          <img className="login-logo" src="/tppl.png" alt="TPL" />
          <h1 className="hero-title">Admin Sign In</h1>

          {!sent && (
            <>
              <label className="field">
                <span className="field-label">Email</span>
                <input
                  className="input"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  autoComplete="email"
                  placeholder="you@example.com"
                  required
                />
              </label>
              <button className="btn btn--primary" type="submit" disabled={requestOtp.isPending}>
                {requestOtp.isPending ? 'Sending…' : 'Send code'}
              </button>
            </>
          )}

          {sent && (
            <>
              <p className="state">
                We sent a 6-digit code to <strong>{email}</strong>.
              </p>
              <label className="field">
                <span className="field-label">Verification code</span>
                <input
                  className="input"
                  inputMode="numeric"
                  autoComplete="one-time-code"
                  maxLength={6}
                  value={token}
                  onChange={(e) => setToken(e.target.value.replace(/\D/g, ''))}
                  placeholder="000000"
                  required
                />
              </label>
              <button
                className="btn btn--primary"
                type="submit"
                disabled={verifyOtp.isPending || token.length < 6}
              >
                {verifyOtp.isPending ? 'Verifying…' : 'Verify & sign in'}
              </button>
              <button
                className="btn"
                type="button"
                onClick={() => {
                  setSent(false)
                  setToken('')
                  verifyOtp.reset()
                  requestOtp.reset()
                }}
              >
                Use a different email
              </button>
            </>
          )}

          {error && <p className="state state--error">{error.message}</p>}
        </form>
      </main>
      <Footer />
    </>
  )
}
