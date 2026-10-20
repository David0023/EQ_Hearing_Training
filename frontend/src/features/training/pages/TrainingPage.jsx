import { TrainingSessionList  } from '../components/TrainingSessionList'
import { Header } from '../../../components/layout/Header'

export function TrainingPage() {
    return (
        <>
            <Header />
            <h2 className="page-title">Training</h2>
            <TrainingSessionList />
        </>
    )
}
