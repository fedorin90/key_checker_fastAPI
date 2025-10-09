import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../../api/axios'
import { toast } from 'react-toastify'

const VerifyEmail = () => {
  const { token } = useParams()
  const navigate = useNavigate()

  useEffect(() => {
    const verifyEmail = async () => {
      try {
        const response = await api.get(`auth/activate/${token}`)

        toast.success('Activation successful! Please log in.')
        navigate('/login')
      } catch (err) {
        const detail = err.response?.data?.detail

        if (detail === 'Activation token expired') {
          toast.error('Activation token expired')
          navigate('/auth/resend-activation/')
        } else {
          toast.error(detail || 'Ошибка активации')
          navigate('/')
        }
      }
    }

    verifyEmail()
  }, [token, navigate])

  return <div></div>
}

export default VerifyEmail
