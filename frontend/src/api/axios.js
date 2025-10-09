import axios from 'axios'
import { Cookies } from 'react-cookie'

const cookies = new Cookies()
const API_URL = process.env.REACT_APP_API_URL

// Создаём экземпляр axios
const api = axios.create({
  baseURL: `${API_URL}/`,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
})

// 👉 Перехватчик запроса
api.interceptors.request.use((config) => {
  const token = cookies.get('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}` // Bearer токен
  }
  return config
})

// 👉 Перехватчик ответа
api.interceptors.response.use(
  (response) => response, // если всё ок — просто возвращаем ответ
  (error) => {
    if (error.response?.status === 401) {
      // Удаляем токен из cookie
      cookies.remove('auth_token', { path: '/' })

      // Удаляем токен из axios
      delete api.defaults.headers.Authorization

      // Перенаправляем на страницу логина
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }

      // Можно вернуть ответ, чтобы не крашился код
      return Promise.resolve(error.response)
    }

    // Остальные ошибки пробрасываем дальше
    return Promise.reject(error)
  }
)

// 👉 Глобальный перехватчик необработанных ошибок
window.addEventListener('unhandledrejection', (event) => {
  if (event.reason?.response?.status === 401) {
    event.preventDefault()
  }
})

// 👉 Функция входа через Google
const loginWithGoogle = async (googleAccessToken) => {
  try {
    const response = await axios.post(`${API_URL}/auth/google/`, {
      access_token: googleAccessToken,
    })
    return response.data.access_token
  } catch (error) {
    console.error('Google login error:', error)
  }
}

export { api, loginWithGoogle }
