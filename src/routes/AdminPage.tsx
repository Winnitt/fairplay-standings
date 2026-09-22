import { Navigate, useParams } from 'react-router'
import { NavBar } from '@/components/NavBar'
import { Footer } from '@/components/Footer'
import { AdminTeamRow } from '@/components/AdminTeamRow'
import { useIsAdmin, useTeams, useUpdateTeam } from '@/hooks/useTeams'
import { useAuthContext } from '@/lib/AuthProvider'
import { supabase } from '@/lib/supabase'
import { GENDER_LABELS, SEASON, isGender, type Gender } from '@/types/database'

export function AdminPage() {
  const { gender } = useParams()
  const { session, loading } = useAuthContext()

  if (loading) return <p className="state">Loading…</p>
  if (!session) return <Navigate to="/admin" replace />
  if (!isGender(gender)) return <Navigate to="/admin/men" replace />

  return <AdminEditor gender={gender} />
}

function AdminEditor({ gender }: { gender: Gender }) {
  const { data: teams, isPending, error } = useTeams(gender)
  const { data: isAdmin, isPending: checkingAdmin } = useIsAdmin()
  const updateTeam = useUpdateTeam(gender)

  if (checkingAdmin) return <p className="state">Checking permissions…</p>

  if (!isAdmin) {
    return (
      <main className="page page--centered">
        <div className="card">
          <h1 className="hero-title">Not an admin</h1>
          <p className="state">
            This account is signed in but is not listed in <code>fairplay.admins</code>.
          </p>
          <button className="btn" type="button" onClick={() => supabase.auth.signOut()}>
            Sign out
          </button>
        </div>
      </main>
    )
  }

  return (
    <>
      <NavBar basePath="/admin" />
      <main className="page">
        <header className="hero">
          <p className="eyebrow">{SEASON} · Admin</p>
          <h1 className="hero-title">{GENDER_LABELS[gender]} Fairplay</h1>
          <button className="btn" type="button" onClick={() => supabase.auth.signOut()}>
            Sign out
          </button>
        </header>

        {isPending && <p className="state">Loading teams…</p>}
        {error && <p className="state state--error">{error.message}</p>}
        {updateTeam.error && <p className="state state--error">{updateTeam.error.message}</p>}

        {teams?.map((team) => (
          <AdminTeamRow
            key={team.id}
            team={team}
            saving={updateTeam.isPending && updateTeam.variables?.id === team.id}
            onSave={(edit) => updateTeam.mutate(edit)}
          />
        ))}
      </main>
      <Footer />
    </>
  )
}
