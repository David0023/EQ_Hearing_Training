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

export function setAccessToken(token) {
  accessToken = token
}

privateApi.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`
  }
  return config
})

for (const api of [publicApi, privateApi]) {
  api.interceptors.response.use(
    (response) => response.data,
    (error) => Promise.reject(error),
  )
}
