import { privateApi } from '../../../api/client'

export function getRecentSessions(page=1, page_size=20) {
    return privateApi.get('/api/v1/training/sessions/recent', {
        params: {
            page, page_size
        }
    })
}

export function createSession(
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
    // TODO: For Guest users, do not create session in db but provide something else.
}
