import { useState } from 'react'

interface Props {
  src: string
  alt: string
  fallback: string
}

/** Falls back to the short name — women's logos are still remote and may 404. */
export function TeamLogo({ src, alt, fallback }: Props) {
  const [failed, setFailed] = useState(false)

  if (!src || failed) {
    return <span className="team-logo team-logo--text">{fallback}</span>
  }

  return (
    <img
      className="team-logo"
      src={src}
      alt={alt}
      loading="lazy"
      onError={() => setFailed(true)}
    />
  )
}
