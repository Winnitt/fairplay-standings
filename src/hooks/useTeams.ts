import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { supabase } from '@/lib/supabase'
import { useAuthContext } from '@/lib/AuthProvider'
import type { Gender, Team, TeamEdit } from '@/types/database'

/**
 * Ranking is ordered by Postgres, not here: `avg_fp` is a generated column
 * and the sort is backed by an index, so the client never re-derives it.
 */
export function useTeams(gender: Gender) {
  return useQuery({
    queryKey: ['teams', gender],
    queryFn: async (): Promise<Team[]> => {
      const { data, error } = await supabase
        .from('teams')
        .select('*')
        .eq('gender', gender)
        .order('avg_fp', { ascending: false })
        .order('fairplay_points', { ascending: false })
        .order('name', { ascending: true })

      if (error) throw error
      return data as Team[]
    },
    staleTime: 60_000,
  })
}

export function useUpdateTeam(gender: Gender) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, ...edit }: TeamEdit & { id: string }) => {
      const { data, error } = await supabase
        .from('teams')
        .update(edit)
        .eq('id', id)
        .select()

      if (error) throw error
      // RLS filters non-admins to zero rows rather than raising.
      if (!data || data.length === 0) {
        throw new Error('Update rejected — your account is not a fairplay admin.')
      }
      return data[0] as Team
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['teams', gender] })
    },
  })
}

/** Admin membership is a row in fairplay.admins, readable only by its owner. */
export function useIsAdmin() {
  const { session } = useAuthContext()
  const userId = session?.user.id

  return useQuery({
    queryKey: ['is-admin', userId],
    enabled: Boolean(userId),
    queryFn: async () => {
      const { data, error } = await supabase
        .from('admins')
        .select('user_id')
        .eq('user_id', userId!)
        .maybeSingle()

      if (error) throw error
      return data !== null
    },
  })
}
