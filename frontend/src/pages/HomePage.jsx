import { Header } from "../components/layout/Header"
import { TrainingSessionList } from "../features/training/components/TrainingSessionList"

export function HomePage() {
  return (
    <>
      <Header />
      <main>
        <h1>EQ Hearing Training</h1>
        <TrainingSessionList />
      </main>
    </>
  )
}
