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
    </main>
  )
}
