import { TrainingSessionList  } from '../components/TrainingSessionList'
import { Header } from '../../../components/layout/Header'

export function TrainingPage() {
    return (
        <>
            <Header />
            <h2>Training</h2>
            <TrainingSessionList />
        </>
    )
}
