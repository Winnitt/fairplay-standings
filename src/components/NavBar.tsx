import { NavLink } from 'react-router'
import { GENDERS, GENDER_LABELS } from '@/types/database'

export function NavBar({ basePath = '' }: { basePath?: string }) {
  return (
    <nav className="nav">
      <img className="nav-brand" src="/tppl.png" alt="TPL" />
      <div className="nav-tabs">
        {GENDERS.map((gender) => (
          <NavLink
            key={gender}
            to={`${basePath}/${gender}`}
            className={({ isActive }) => (isActive ? 'chip chip--active' : 'chip')}
          >
            {GENDER_LABELS[gender]}
          </NavLink>
        ))}
      </div>
    </nav>
  )
}
