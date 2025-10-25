import { BrowserRouter as Router, Route, Routes } from 'react-router-dom'
import { ToastContainer } from 'react-toastify'
import { AuthProvider } from './context/AuthContext'
import PrivateRoute from './utils/PrivateRoute'
import StaffRoute from './utils/StaffRoute'
import Header from './components/Header'
import Home from './components/Home'
import Login from './components/User/Login'
import Register from './components/User/Register'
import VerifyEmail from './components/User/VerifyEmail'
import Profile from './components/User/Profile'
import ResendActivation from './components/User/ResendActivation'
import TermsAndConditions from './components/TermsAndConditions'
import PasswordReset from './components/User/PasswordReset'
// import KeysCheck from './components/KeysCheck/KeysCheck'
// import MSManage from './components/KeysCheck/MSManage'
import Proxies from './components/KeysCheck/Proxies'

function App() {
  return (
    <Router>
      <AuthProvider>
        <Header />
        <Routes>
          {/*Private urls */}
          <Route element={<PrivateRoute />}>
            <Route path="/profile" element={<Profile />} />
            {/* <Route path="/keys-check" element={<KeysCheck />} /> */}
          </Route>
          {/* Staff urls */}
          <Route element={<StaffRoute />}>
            {/* <Route path="/ms-manage" element={<MSManage />} /> */}
            <Route path="/proxies" element={<Proxies />} />
          </Route>
          {/* public urls */}
          <Route path="/" element={<Home />} />
          <Route path="/register" element={<Register />} />
          <Route path="/login" element={<Login />} />
          <Route path="/auth/activate/:token/" element={<VerifyEmail />} />
          <Route
            path="/auth/resend-activation/"
            element={<ResendActivation />}
          />
          <Route path="/password-reset/:token/" element={<PasswordReset />} />
          <Route
            path="/terms-and-conditions"
            element={<TermsAndConditions />}
          />
        </Routes>
        <ToastContainer hideProgressBar position="top-center" />
      </AuthProvider>
    </Router>
  )
}

export default App
