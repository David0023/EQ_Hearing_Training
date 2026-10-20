import { useEffect, useState } from 'react'
import { getFrequencies } from '../api/info'
import './FrequencySelector.css'

function formatLabel(label) {
  return label
    .split('_')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
}

export function FrequencySelector({ setMinFrequency, setMaxFrequency }) {
  const [groups, setGroups] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selected, setSelected] = useState([])
  const [sameEndpoint, setSameEndpoint] = useState(false)

  useEffect(() => {
    let active = true

    getFrequencies()
      .then((data) => {
        if (!active) return

        const seenFrequencies = new Set()
        const uniqueGroups = (data.available_groups ?? [])
          .map((group) => ({
            ...group,
            frequencies: (group.frequencies ?? []).filter((frequency) => {
              if (seenFrequencies.has(frequency)) return false
              seenFrequencies.add(frequency)
              return true
            }),
          }))
          .filter((group) => group.frequencies.length > 0)

        setGroups(uniqueGroups)
      })
      .catch(() => {
        if (active) setError('Could not load available frequencies.')
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => { active = false }
  }, [])

  if (loading) return <p>Loading frequencies…</p>
  if (error) return <p role="alert">{error}</p>

  const min = selected.length ? Math.min(...selected) : null
  const hasRange = selected.length === 2 || sameEndpoint
  const max = hasRange ? Math.max(...selected) : null

  function handleClick(frequency) {
    if (selected.length === 1 && selected[0] === frequency) {
      setSameEndpoint(true)
      setMinFrequency?.(frequency)
      setMaxFrequency?.(frequency)
      return
    }

    const next = selected.length === 0 || hasRange
      ? [frequency]
      : [selected[0], frequency]

    const nextMin = Math.min(...next)
    const nextMax = Math.max(...next)

    setSelected(next)
    setSameEndpoint(false)
    setMinFrequency?.(nextMin)
    setMaxFrequency?.(nextMax)
  }

  return (
    <section className="frequency-selector" aria-label="Frequency range">
      <p className="frequency-selector__summary" aria-live="polite">
        Selected range:{' '}
        {min === null
          ? 'Choose two frequencies'
          : max === null
            ? `${min} Hz — choose the other endpoint`
            : `${min} Hz to ${max} Hz`}
      </p>

      <div
        className="frequency-selector__groups"
        style={{ '--frequency-group-count': Math.max(groups.length, 1) }}
      >
        {groups.map((group) => (
          <div className="frequency-selector__group" key={group.name}>
            <p className="frequency-selector__group-title">{formatLabel(group.name)}</p>
            <div className="frequency-selector__options">
              {group.frequencies.map((frequency) => {
                const isEndpoint = selected.includes(frequency)
                const isBetween =
                  hasRange && frequency >= min && frequency <= max

                return (
                  <button
                    key={frequency}
                    type="button"
                    className={`frequency-selector__button${isBetween ? ' is-in-range' : ''}${isEndpoint ? ' is-endpoint' : ''}`}
                    aria-pressed={isEndpoint}
                    onClick={() => handleClick(frequency)}
                  >
                    {frequency} Hz
                  </button>
                )
              })}
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
