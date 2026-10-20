import { FrequencySelector } from '../components/FrequencySelector'
import { Header } from '../../../components/layout/Header'

export function StartTrainingPage() {
    return (<>
        <Header />
        <h2>Start a new training</h2>
        <FrequencySelector />
    </>)
}
