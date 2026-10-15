import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const publicApi = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  withCredentials: true,
})

export const privateApi = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  withCredentials: true,
})

let accessToken = null
let refreshInProgress = null

export function setAccessToken(token) {
  accessToken = token
}

privateApi.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`
  }
  return config
})

publicApi.interceptors.response.use(
    (response) => response.data,
    (error) => Promise.reject(error),
)

privateApi.interceptors.response.use(
    (response) => response.data,
    async (error) => {
        const originalRequest = error.config
        if (error.response?.status != 401 || originalRequest._retried) {
            return Promise.reject(error)
        }
        originalRequest._retried = true

        try {
            if (!refreshInProgress) {
                refreshInProgress = publicApi
                .post('/auth/refresh')
                .then((response) => {
                    setAccessToken(response.data.access_token)
                })
                .finally(() => {
                    refreshInProgress = null
                })
            }
            await refreshInProgress
            originalRequest.headers.Authorization = `Bearer ${accessToken}`

            return privateApi(originalRequest)
        } catch (refreshError) {
            setAccessToken(null)
            return Promise.reject(refreshError)
        }
    },
)
