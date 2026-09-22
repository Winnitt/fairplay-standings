import { useMutation } from '@tanstack/react-query'
import { supabase } from '@/lib/supabase'

/**
 * Email OTP, matching Football OS. `shouldCreateUser: false` keeps this an
 * admin gate rather than a sign-up form — an unknown email is rejected
 * instead of silently creating an auth user.
 */
export function useRequestOtp() {
  return useMutation({
    mutationFn: async (email: string) => {
      const { error } = await supabase.auth.signInWithOtp({
        email,
        options: { shouldCreateUser: false },
      })
      if (error) {
        throw new Error(
          error.message.toLowerCase().includes('signups not allowed')
            ? 'No account for that email. Ask an organizer to add you first.'
            : error.message,
        )
      }
    },
  })
}

export function useVerifyOtp() {
  return useMutation({
    mutationFn: async ({ email, token }: { email: string; token: string }) => {
      const { error } = await supabase.auth.verifyOtp({ email, token, type: 'email' })
      if (error) throw error
    },
  })
}
