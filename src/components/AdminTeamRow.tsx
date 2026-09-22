import { useState, type FormEvent } from 'react'
import { TeamLogo } from './TeamLogo'
import type { Team } from '@/types/database'

interface Props {
  team: Team
  onSave: (edit: { id: string; name: string; logo_url: string; matches: number; fairplay_points: number }) => void
  saving: boolean
}

export function AdminTeamRow({ team, onSave, saving }: Props) {
  const [name, setName] = useState(team.name)
  const [logoUrl, setLogoUrl] = useState(team.logo_url)
  const [matches, setMatches] = useState(String(team.matches))
  const [points, setPoints] = useState(String(team.fairplay_points))

  const dirty =
    name !== team.name ||
    logoUrl !== team.logo_url ||
    matches !== String(team.matches) ||
    points !== String(team.fairplay_points)

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    onSave({
      id: team.id,
      name: name.trim(),
      logo_url: logoUrl.trim(),
      matches: Number(matches),
      fairplay_points: Number(points),
    })
  }

  return (
    <form className="card admin-row" onSubmit={handleSubmit}>
      <div className="team">
        <TeamLogo src={team.logo_url} alt={team.name} fallback={team.short_name} />
        <div className="team-names">
          <span className="team-short">{team.short_name}</span>
          <span className="team-full">{team.name}</span>
        </div>
        <span className="stat stat--hero">{Number(team.avg_fp).toFixed(3)}</span>
      </div>

      <label className="field">
        <span className="field-label">Team name</span>
        <input className="input" value={name} onChange={(e) => setName(e.target.value)} required />
      </label>

      <div className="admin-row-numbers">
        <label className="field">
          <span className="field-label">Matches</span>
          <input
            className="input"
            type="number"
            min="0"
            value={matches}
            onChange={(e) => setMatches(e.target.value)}
            required
          />
        </label>
        <label className="field">
          <span className="field-label">Fairplay points</span>
          <input
            className="input"
            type="number"
            min="0"
            value={points}
            onChange={(e) => setPoints(e.target.value)}
            required
          />
        </label>
      </div>

      <label className="field">
        <span className="field-label">Logo URL</span>
        <input className="input" value={logoUrl} onChange={(e) => setLogoUrl(e.target.value)} />
      </label>

      <button className="btn btn--primary" type="submit" disabled={!dirty || saving}>
        {saving ? 'Saving…' : dirty ? 'Save changes' : 'Saved'}
      </button>
    </form>
  )
}
