import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../../api/axios'
import { toast } from 'react-toastify'
import { Form, Col, Container, Row, Button } from 'react-bootstrap'

const ResendActivation = () => {
  const [email, setEmail] = useState('')
  const navigate = useNavigate()

  const handleResend = async () => {
    try {
      const response = await api.post('/auth/resend-activation/', { email })
      toast.success(response?.data?.message)
      navigate('/login')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Error sending activation link')
    }
  }

  return (
    <Container className="mt-5">
      <Row>
        <Col></Col>
        <Col xs={4}>
          <h1>Отправка кода подтверждения</h1>
          <Form
            onSubmit={(e) => {
              e.preventDefault()
              handleResend()
            }}
          >
            <Form.Group className="mb-3" controlId="formBasicEmail">
              <Form.Label>Email</Form.Label>
              <Form.Control
                type="email"
                placeholder="Введи свой email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </Form.Group>

            <p />
            <Button variant="primary" type="submit" style={{ width: '100%' }}>
              Отправить
            </Button>
          </Form>
        </Col>
        <Col></Col>
      </Row>
    </Container>
  )
}

export default ResendActivation
