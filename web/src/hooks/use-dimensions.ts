import { useLayoutEffect, useState, type RefObject } from 'react'

export type Dimensions = { width: number; height: number }

/**
 * Measures an element and keeps its size up to date.
 *
 * Returns { width: 0, height: 0 } until the element has been measured, so charts
 * can wait for real sizes before drawing. ResizeObserver fires whenever the
 * element changes size, not just when the window does, so it also catches layout
 * changes such as a sidebar opening.
 */
export function useDimensions(ref: RefObject<HTMLElement | null>): Dimensions {
  const [dimensions, setDimensions] = useState<Dimensions>({ width: 0, height: 0 })

  useLayoutEffect(() => {
    const element = ref.current
    if (!element) return

    const observer = new ResizeObserver(([entry]) => {
      const { width, height } = entry.contentRect
      setDimensions({ width, height })
    })
    observer.observe(element)

    // Tidy up when the component is removed, so the observer doesn't leak.
    return () => observer.disconnect()
  }, [ref])

  return dimensions
}
