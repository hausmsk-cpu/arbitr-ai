import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

// Автоподстановка Bearer-токена
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('Arbitr AI_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api