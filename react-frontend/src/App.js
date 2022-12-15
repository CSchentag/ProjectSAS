import Container from 'react-bootstrap/Container';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import FlashProvider from './contexts/FlashProvider';
import ApiProvider from './contexts/ApiProvider';
import UserProvider from './contexts/UserProvider';
import Header from './components/Header';
import PublicRoute from './components/PublicRoute';
import PrivateRoute from './components/PrivateRoute';
import FeedPage from './pages/FeedPage';
import TablePage from './pages/TablePage';
import UserPage from './pages/UserPage';
import AccountantPage from './pages/AccountantPage';
import EditUserPage from './pages/EditUserPage';
import ChangePasswordPage from './pages/ChangePasswordPage';
import LoginPage from './pages/LoginPage';
import RegistrationPage from './pages/RegistrationPage';
import ResetRequestPage from './pages/ResetRequestPage';
import ResetPage from './pages/ResetPage';
import { library } from "@fortawesome/fontawesome-svg-core";
import { fas } from "@fortawesome/free-solid-svg-icons";

library.add(fas);

export default function App() {
  return (
    <Container fluid className="App">
      <BrowserRouter>
        <FlashProvider>
          <ApiProvider>
            <UserProvider>
              <Header />
              <Routes>
                <Route path="/login" element={
                  <PublicRoute><LoginPage /></PublicRoute>
                } />
                <Route path="/register" element={
                  <PublicRoute><RegistrationPage /></PublicRoute>
                } />
                <Route path="/reset-request" element={
                  <PublicRoute><ResetRequestPage /></PublicRoute>
                } />
                <Route path="/reset" element={
                  <PublicRoute><ResetPage /></PublicRoute>
                } />
                <Route path="*" element={
                  <PrivateRoute>
                    <Routes>
                      <Route path="/" element={<FeedPage />} />
                      <Route path="/table" element={<TablePage />} />
                      <Route path="/user/:username" element={<UserPage />} />
                      <Route path="/accountants/:username" element={<AccountantPage />} />
                      <Route path="/edit" element={<EditUserPage />} />
                      <Route path="/password" element={<ChangePasswordPage />} />
                      <Route path="*" element={<Navigate to="/" />} />
                    </Routes>
                  </PrivateRoute>
                } />
              </Routes>
            </UserProvider>
          </ApiProvider>
        </FlashProvider>
      </BrowserRouter>
    </Container>
  );
}