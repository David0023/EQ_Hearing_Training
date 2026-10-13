import { privateApi, publicApi } from './client'

let refreshPromise

export async function login(username, password) {
  const form = new URLSearchParams({ username, password, grant_type: 'password' })
  return publicApi.post('/auth/login', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
}

export async function refreshAccessToken() {
  if (!refreshPromise) {
    refreshPromise = publicApi.post('/auth/refresh').finally(() => {
      refreshPromise = undefined
    })
  }
  return refreshPromise
}

export function logout() {
  return privateApi.post('/auth/logout')
}

export function signup(username, email, password) {
  return publicApi.post('/auth/register', { username, email, password })
}
