import { useEffect, useState } from 'react'
import { Link } from 'react-router'
import { useAuth } from '../../auth/AuthContext'
import { getRecentSessions } from '../api/sessions'
import './TrainingSessionList.css'

function formatDate(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '—'
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date)
}

function formatLabel(value) {
  return value
    .split('_')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
}

export function TrainingSessionList() {
  const { isAuthenticated, isLoading: authLoading } = useAuth()
  const [sessions, setSessions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (authLoading) return undefined
    if (!isAuthenticated) {
      setLoading(false)
      setSessions([])
      return undefined
    }

    let active = true
    setLoading(true)
    setError('')

    getRecentSessions()
      .then((data) => {
        if (active) setSessions(data.sessions ?? [])
      })
      .catch(() => {
        if (active) setError('Your recent sessions could not be loaded.')
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => { active = false }
  }, [authLoading, isAuthenticated])

  return (
    <section className="training-session-list" aria-labelledby="recent-sessions-title">
      <div className="training-session-list__heading">
        <div>
          <p className="training-session-list__eyebrow">Your practice</p>
          <h2 id="recent-sessions-title">Recent sessions</h2>
        </div>
        {isAuthenticated && <Link to="/training/start">Start training</Link>}
      </div>

      {authLoading || loading ? (
        <p className="training-session-list__message" role="status">Loading sessions…</p>
      ) : !isAuthenticated ? (
        <p className="training-session-list__message">
          <Link to="/login">Log in</Link> to see your training history.
        </p>
      ) : error ? (
        <p className="training-session-list__message" role="alert">{error}</p>
      ) : sessions.length === 0 ? (
        <p className="training-session-list__message">No training sessions yet. Start a session to see your progress here.</p>
      ) : (
        <ul className="training-session-list__items">
          {sessions.map(({ session, answered_count: answeredCount, correct_count: correctCount, accuracy }) => (
            <li className="training-session-card" key={session.id}>
              <div className="training-session-card__topline">
                <h3>{formatLabel(session.question_type)}</h3>
                <span className={`training-session-card__status training-session-card__status--${session.session_status}`}>
                  {formatLabel(session.session_status)}
                </span>
              </div>
              <p className="training-session-card__date">{formatDate(session.started_at)}</p>
              <dl className="training-session-card__stats">
                <div><dt>Questions</dt><dd>{answeredCount} / {session.num_questions}</dd></div>
                <div><dt>Correct</dt><dd>{correctCount}</dd></div>
                <div><dt>Accuracy</dt><dd>{Math.round(accuracy)}%</dd></div>
              </dl>
              <p className="training-session-card__range">
                {session.min_frequency}–{session.max_frequency} Hz <span aria-hidden="true">·</span> Gain {session.gain_level} dB
              </p>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
