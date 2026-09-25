import { Navigate, useParams } from 'react-router'
import { NavBar } from '@/components/NavBar'
import { Footer } from '@/components/Footer'
import { TeamLogo } from '@/components/TeamLogo'
import { useTeams } from '@/hooks/useTeams'
import { GENDER_TITLES, SEASON, isGender } from '@/types/database'

export function StandingsPage() {
  const { gender } = useParams()

  if (!isGender(gender)) return <Navigate to="/men" replace />

  return <Standings gender={gender} />
}

function Standings({ gender }: { gender: 'men' | 'women' }) {
  const { data: teams, isPending, error } = useTeams(gender)

  return (
    <>
      <NavBar />
      <main className="page">
        <header className="hero">
          <p className="eyebrow">TPL Fairplay Rankings</p>
          <h1 className="hero-title">{GENDER_TITLES[gender]}</h1>
          <p className="hero-season">{SEASON}</p>
        </header>

        <section className="card">
          {isPending && <p className="state">Loading standings…</p>}
          {error && <p className="state state--error">{error.message}</p>}
          {teams && teams.length === 0 && <p className="state">No teams found.</p>}

          {teams && teams.length > 0 && (
            <table className="standings">
              <thead>
                <tr>
                  <th className="col-rank">#</th>
                  <th>Team</th>
                  <th className="col-num">M</th>
                  <th className="col-num">FP</th>
                  <th className="col-num">AVG</th>
                </tr>
              </thead>
              <tbody>
                {teams.map((team, index) => (
                  <tr key={team.id}>
                    <td className={index < 3 ? 'col-rank rank rank--top' : 'col-rank rank'}>
                      {index + 1}
                    </td>
                    <td>
                      <div className="team">
                        <TeamLogo src={team.logo_url} alt={team.name} fallback={team.short_name} />
                        <div className="team-names">
                          <span className="team-short">{team.short_name}</span>
                          <span className="team-full">{team.name}</span>
                        </div>
                      </div>
                    </td>
                    <td className="col-num stat">{team.matches}</td>
                    <td className="col-num stat">{team.fairplay_points}</td>
                    <td className="col-num stat stat--hero">{Number(team.avg_fp).toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      </main>
      <Footer />
    </>
  )
}
