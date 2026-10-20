import { Header } from "../components/layout/Header"
import { TrainingSessionList } from "../features/training/components/TrainingSessionList"

export function HomePage() {
  return (
    <>
      <Header />
      <main className="home-page">
        <h1 className="home-page__title">EQ Hearing Training</h1>
        <TrainingSessionList />
      </main>
    </>
  )
}
