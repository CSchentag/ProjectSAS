import Navbar from 'react-bootstrap/Navbar';
import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import NavDropdown from 'react-bootstrap/NavDropdown';
import Image from 'react-bootstrap/Image';
import Spinner from 'react-bootstrap/Spinner';
import { NavLink } from 'react-router-dom';
import { useUser } from '../contexts/UserProvider';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'

export default function Header() {
  const { user, logout } = useUser();

  return (
    <Navbar bg="light" sticky="top" className="Header">
      <Container>
        <Navbar.Brand>
            Sask Accountant Search Engine&nbsp;&nbsp;
            <FontAwesomeIcon icon="fa-solid fa-briefcase" />
             </Navbar.Brand>
        <Nav.Item>
        <Nav.Link as={NavLink} to="/" end>Accountant List</Nav.Link>
      </Nav.Item>
      <Nav.Item>
        <Nav.Link as={NavLink} to="/table">Accountant Search</Nav.Link>
      </Nav.Item>
        <Nav.Item>
        <Nav.Link as={NavLink} to="/" end>About Us</Nav.Link>
      </Nav.Item>
      <Nav.Item>
        <Nav.Link as={NavLink} to="/table">Contact Us</Nav.Link>
      </Nav.Item>

      <Nav >
          {user === undefined ?
            <Spinner animation="border" />
          :

            <>
              {user !== null &&
                <div className="justify-content-end">
                  <NavDropdown title={
                    <Image src={user.avatar_url + '&s=32'} roundedCircle />
                  } align="end">
                    <NavDropdown.Item as={NavLink} to={'/user/' + user.username}>
                      Profile
                    </NavDropdown.Item>
                    <NavDropdown.Divider />
                    <NavDropdown.Item as={NavLink} to="/password">
                      Change Password
                    </NavDropdown.Item>
                    <NavDropdown.Item onClick={logout}>
                      Logout
                    </NavDropdown.Item>
                  </NavDropdown>
                </div>
              }
            </>
          }
        </Nav>
      </Container>
    </Navbar>
  );
}