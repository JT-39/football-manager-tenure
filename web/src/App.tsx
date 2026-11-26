import { ResponsiveBarplot } from '@/components/charts/barplot'
import { exampleBarData } from '@/data/example-barplot'

// The page is one narrow column (700px at most, centred). Charts can break out
// of it later if they need the full width.
export default function App() {
  return (
    <main className="mx-auto max-w-[700px] px-4 pb-24">
      <h1 className="pt-16 text-5xl font-bold">Managerial tenure</h1>
      <p className="mt-6">
        How long Premier League managers stay, and what happens to their clubs while they are in
        charge. This is a starting page with example data, ready for our own charts.
      </p>

      <h2 className="mt-24 mb-6 text-3xl font-bold">An example barplot</h2>
      <p className="mb-6">
        The chart below is responsive: resize the window and it redraws to fit.
      </p>
      {/* A chart needs a container with a height, or it will not appear. See the d3 skill. */}
      <div style={{ height: 400 }}>
        <ResponsiveBarplot data={exampleBarData} />
      </div>

      {/* Credit for the Wikipedia data (CC BY-SA 4.0 requires attribution and a licence link). */}
      <footer className="mt-24 border-t pt-6 text-sm text-muted-foreground">
        <p>
          Manager data from{' '}
          <a className="underline" href="https://en.wikipedia.org/wiki/List_of_Premier_League_managers">
            Wikipedia: List of Premier League managers
          </a>{' '}
          by Wikipedia contributors, licensed under{' '}
          <a className="underline" href="https://creativecommons.org/licenses/by-sa/4.0/">
            CC BY-SA 4.0
          </a>
          . The bars above are example data, not the managers' data.
        </p>
      </footer>
    </main>
  )
}
