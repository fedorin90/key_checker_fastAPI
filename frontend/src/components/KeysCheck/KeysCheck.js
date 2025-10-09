import React, { useEffect, useState } from 'react'
import { IoMdCheckboxOutline } from 'react-icons/io'
import { MdOutlineNavigateNext } from 'react-icons/md'
import { toast } from 'react-toastify'
import {
  Container,
  Form,
  Col,
  InputGroup,
  Card,
  Row,
  Button,
  Alert,
  Table,
  ProgressBar,
} from 'react-bootstrap'
import { api } from '../../api/axios'
import {
  createKeys,
  checkKeys,
  fetchLastSessionKeys,
} from '../../api/KeysCheckerService'

const KeysCheck = () => {
  const [input, setInput] = useState('')
  const [validKeys, setValidKeys] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [progress, setProgress] = useState({ total: 0, checked: 0, percent: 0 })
  const [showOnlyNotActivated, setShowOnlyNotActivated] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    const lines = input.split('\n')

    const cleaned = lines
      .map((line) =>
        line
          .replace(/[^A-Z0-9]/gi, '')
          .toUpperCase()
          .trim()
      )
      .filter((key) => key.length === 25)

    // if (cleaned.length > 200) {
    //   setError('Превышен лимит: максимум 200 ключей.')
    //   setLoading(false)
    //   return
    // }

    if (cleaned.length === 0) {
      setError('Нет ни одного корректного ключа.')
      setLoading(false)
      return
    }

    const keyObjects = cleaned.map((key) => ({ key }))

    try {
      const res = await createKeys(keyObjects)

      setValidKeys(res)
    } catch (error) {
      toast.error(error.message)
    } finally {
      setLoading(false)
    }
  }

  const handleCheck = async () => {
    try {
      const sessionId = validKeys[0]?.session_id
      if (!sessionId) return

      await checkKeys(sessionId)

      // Запускаем опрос прогресса
      let intervalId = setInterval(async () => {
        try {
          const res = await api.get(`/api/progress/${sessionId}/`)
          setProgress(res.data)
          // 🔁 обновляем список ключей при любом изменении прогресса
          const updatedKeys = await fetchLastSessionKeys()
          setValidKeys(updatedKeys)

          // Когда 100%, останавливаем опрос
          if (res.data.percent >= 100) {
            clearInterval(intervalId)

            // Повторно загрузим актуальные ключи после завершения
            const updatedKeys = await fetchLastSessionKeys()
            setValidKeys(updatedKeys)
          }
        } catch (err) {
          console.error('Ошибка получения прогресса', err)
          clearInterval(intervalId)
        }
      }, 1000)
    } catch (error) {
      toast.error(error.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const getLastSessionKeys = async () => {
      setLoading(true)
      try {
        const res = await fetchLastSessionKeys()
        setValidKeys(res)

        // Попробуем восстановить прогресс
        const sessionId = res[0]?.session_id
        if (sessionId) {
          const progressRes = await api.get(`/api/progress/${sessionId}/`)
          setProgress(progressRes.data)

          // Если прогресс ещё не 100%, возобновим polling
          if (progressRes.data.percent < 100) {
            const intervalId = setInterval(async () => {
              try {
                const res = await api.get(`/api/progress/${sessionId}/`)
                setProgress(res.data)

                if (res.data.percent >= 100) {
                  clearInterval(intervalId)
                  const updatedKeys = await fetchLastSessionKeys()
                  setValidKeys(updatedKeys)
                }
              } catch (err) {
                console.error('Ошибка получения прогресса', err)
                clearInterval(intervalId)
              }
            }, 1000)
          }
        }
      } catch (error) {
        toast.error(error.message)
      } finally {
        setLoading(false)
      }
    }

    getLastSessionKeys()
  }, [])

  return (
    <Container fluid="md" className="my-5 ">
      <Card>
        <Row>
          <Col></Col>
          <Col xs={12} md={10} xl={9} className="overflow-auto">
            <div className="position-relative px-3 py-2">
              <h3 className="text-center m-5">
                Шаг 1 - Форматирование списка.
              </h3>
              <Form onSubmit={handleSubmit} className="mb-2">
                <Form.Label htmlFor="basic-url">
                  Введите список ключей в формате: XXXXX-XXXXX-XXXXX-XXXXX-XXXXX
                  или XXXXXXXXXXXXXXXXXXXXXXXXX разделенные переносом строки.
                  Максимум: 200 шт.
                </Form.Label>
                <InputGroup className="mb-2">
                  <InputGroup.Text>Список ключей:</InputGroup.Text>
                  <Form.Control
                    as="textarea"
                    rows={10}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="xxxxx-xxxxx-xxxxx-xxxxx-xxxxx&#10;xxxxx-xxxxx-xxxxx-xxxxx-xxxxx&#10;xxxxx-xxxxx-xxxxx-xxxxx-xxxxx&#10;xxxxx-xxxxx-xxxxx-xxxxx-xxxxx&#10;"
                  />
                </InputGroup>
                <Button variant="primary" type="submit">
                  Продолжить <MdOutlineNavigateNext />
                </Button>

                {error && (
                  <Alert variant="danger" className="mt-3">
                    {error}
                  </Alert>
                )}
                {!loading &&
                  Array.isArray(validKeys) &&
                  validKeys.length > 0 && (
                    <Alert variant="success" className="mt-3">
                      Найдено корректных ключей: {validKeys.length}
                    </Alert>
                  )}
              </Form>
              <h3 className="text-center m-5">Шаг 2 - Проверка ключей.</h3>
              <Button variant="primary" type="submit" onClick={handleCheck}>
                Проверить <IoMdCheckboxOutline />
              </Button>
              <Form.Check
                type="checkbox"
                id="show-only-not-activated"
                label="Показать только неактивированные ключи"
                checked={showOnlyNotActivated}
                onChange={(e) => setShowOnlyNotActivated(e.target.checked)}
                className="mt-4"
              />

              {progress.total > 0 && (
                <div className="my-3">
                  <p>
                    Проверено {progress.checked} из {progress.total} (
                    {progress.percent}%)
                  </p>
                  <ProgressBar
                    now={progress.percent}
                    label={`${progress.percent}%`}
                  />
                </div>
              )}
              <Table striped bordered hover responsive className="mt-2">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Key</th>
                    <th>Проверен</th>
                    <th>Активирован</th>
                    <th>Ошибка</th>
                    {/* <th>Активирован на</th>
                    <th>Дата активации</th> */}
                  </tr>
                </thead>

                <tbody>
                  {validKeys
                    .filter(
                      (item) =>
                        !showOnlyNotActivated || item.is_activated === false
                    )
                    .map((item, index) => (
                      <tr key={item.id}>
                        <td>{index + 1}</td>
                        <td>{item.key}</td>
                        <td>{item.checked ? 'Yes' : 'No'}</td>
                        <td>{item.is_activated ? 'Yes' : 'No'}</td>
                        <td>{item.error_code}</td>
                        {/* <td>{item.redeemed_by ?? '—'}</td>
                        <td>{item.redeemed_date ?? '—'}</td> */}
                      </tr>
                    ))}
                </tbody>
              </Table>
            </div>
          </Col>
          <Col></Col>
        </Row>
      </Card>
    </Container>
  )
}

export default KeysCheck
