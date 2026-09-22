import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing VITE_SUPABASE_URL or VITE_SUPABASE_ANON_KEY env variables')
}

/**
 * Scoped to the `fairplay` schema — this app never touches Football OS's
 * `public` tables. Auth is unaffected by the schema setting.
 */
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  db: { schema: 'fairplay' },
})
