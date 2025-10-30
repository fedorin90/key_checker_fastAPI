import React, { useEffect, useState } from 'react'
import {
  Table,
  Button,
  Modal,
  Form,
  Container,
  Row,
  Col,
} from 'react-bootstrap'
import { toast } from 'react-toastify'
import { api } from '../../api/axios'
import { useContext } from 'react'
import AuthContext from '../../context/AuthContext'

const MSManage = () => {
  const { user } = useContext(AuthContext)
  const [newAccount, setNewAccount] = useState({ email: '', password: '' })
  const [accounts, setAccounts] = useState([])
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState({ email: '', password: '' })
  const [editingId, setEditingId] = useState(null)
  const [bulkText, setBulkText] = useState('')

  const loadAccounts = async () => {
    const res = await api.get('ms_accounts/')
    setAccounts(res.data)
  }

  const handleSave = async () => {
    try {
      if (editingId) {
        await api.put(`ms_accounts/${editingId}/`, form)
        setShowModal(false)
        setForm({ email: '', password: '' })
        setEditingId(null)
        loadAccounts()
      }
    } catch (err) {
      const message = err.response?.data?.detail || 'Faild to save'
      toast.error(message)
    }
  }

  const handleAdd = async () => {
    try {
      await api.post('ms_accounts/', newAccount)
      setNewAccount({ email: '', password: '', note: '' })
      loadAccounts()
    } catch (err) {
      const message = err.response?.data?.detail || 'Failed to dowload'
      toast.error(message)
    }
  }

  const handleBulkUpload = async () => {
    const lines = bulkText.trim().split('\n')
    const accounts = lines
      .map((line) => {
        // разделяем по любому количеству пробелов или табуляций
        const [email, password] = line.trim().split(/\s+/)
        if (!email || !password) return null
        return { email, password }
      })
      .filter(Boolean)

    try {
      const res = await api.post('ms_accounts/bulk/', accounts)
      loadAccounts()
      alert(`Успешно добавлено: ${res.data.length}`)
      setBulkText('')
    } catch (err) {
      const message = err.response?.data?.detail || 'Ошибка загрузки аккаунтов'
      alert(message)
    }
  }

  const handleDelete = async (id) => {
    if (window.confirm('Удалить аккаунт?')) {
      await api.delete(`ms_accounts/${id}/`)
      loadAccounts()
    }
  }

  const handleEdit = (account) => {
    setForm(account)
    setEditingId(account.id)
    setShowModal(true)
  }

  useEffect(() => {
    loadAccounts()
  }, [])

  return (
    <Container>
      <Row className="my-4">
        <Col>
          <h2>Управление аккаунтами Microsoft</h2>
        </Col>
      </Row>

      <Form className="my-3 mb-5">
        <Row className="align-items-end">
          <Col md={3}>
            <Form.Label>Добавить аккаунт</Form.Label>
            <Form.Control
              type="email"
              value={newAccount.email}
              onChange={(e) =>
                setNewAccount({ ...newAccount, email: e.target.value })
              }
              placeholder="Email"
            />
          </Col>
          <Col md={3}>
            <Form.Control
              type="text"
              value={newAccount.password}
              onChange={(e) =>
                setNewAccount({ ...newAccount, password: e.target.value })
              }
              placeholder="Пароль"
            />
          </Col>
          <Col md={3}>
            <Button variant="primary" onClick={handleAdd}>
              Добавить аккаунт
            </Button>
          </Col>
        </Row>
      </Form>

      <Form.Group className="mb-3">
        <Form.Label>
          Массовая загрузка аккаунтов (email[TAB]password)
        </Form.Label>
        <Form.Control
          as="textarea"
          rows={3}
          placeholder="example@example.com	Password123"
          onChange={(e) => setBulkText(e.target.value)}
        />
      </Form.Group>
      <Button variant="success" onClick={handleBulkUpload}>
        Добавить аккаунты
      </Button>

      <Table striped bordered hover className="mt-3">
        <thead>
          <tr>
            <th>Email</th>
            <th>Пароль</th>
            <th>Использован</th>
            <th>Дата последнего использования</th>
            <th>Счетчик использования</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          {accounts.map((acc) => (
            <tr key={acc.id}>
              <td>{acc.email}</td>
              <td>{acc.password}</td>
              <td>{acc.is_used ? 'Да' : 'Нет'}</td>
              <td>{acc.last_used_at ?? '—'}</td>
              <td>{acc.usage_count}</td>

              <td>
                <Button size="sm" onClick={() => handleEdit(acc)}>
                  Редактировать
                </Button>{' '}
                <Button
                  size="sm"
                  variant="danger"
                  onClick={() => handleDelete(acc.id)}
                >
                  Удалить
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>

      <Modal show={showModal} onHide={() => setShowModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Редактировать аккаунт</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Email</Form.Label>
              <Form.Control
                type="email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Пароль</Form.Label>
              <Form.Control
                type="text"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowModal(false)}>
            Отмена
          </Button>
          <Button variant="primary" onClick={handleSave}>
            Сохранить
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  )
}

export default MSManage
