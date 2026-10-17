import { privateApi } from '../../../api/client'

export function createTrainingSession(
    isAuthenticated, numQuestions, questionType, minFreequency,
    maxFrequency, gainLevel
) {
    if (isAuthenticated) {
        return privateApi.post('/api/v1/training/sessions', {
            'num_questions': numQuestions,
            'question_type': questionType,
            'min_freequency': minFreequency,
            'max_frequency': maxFrequency,
            'gain_level': gainLevel,
        })
    }
}
