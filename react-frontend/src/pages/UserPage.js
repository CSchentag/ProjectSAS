import { useState, useEffect } from 'react';
import Stack from 'react-bootstrap/Stack';
import Image from 'react-bootstrap/Image';
import Button from 'react-bootstrap/Button';
import Spinner from 'react-bootstrap/Spinner';
import { useParams, useNavigate } from 'react-router-dom';
import Body from '../components/Body';
import { useApi } from '../contexts/ApiProvider';
import { useUser } from '../contexts/UserProvider';

export default function UserPage() {
  const { username } = useParams();
  const [user, setUser] = useState();
  const [isFollower, setIsFollower] = useState();
  const { user: loggedInUser } = useUser();
  const navigate = useNavigate();
  const api = useApi();

  useEffect(() => {
    (async () => {
      const response = await api.get('/user/' + username);
      if (response.ok) {
        setUser(response.body);
        if (response.body.username === loggedInUser.username) {
          setIsFollower(true)
        }
      }
      else {
        setUser(undefined);
      }
    })();
  }, [username, api, loggedInUser]);

const edit = () => {
    navigate('/edit');
  };

  return (
    <Body sidebar>
      {user === undefined ?
        <Spinner animation="border" />
      :
        <>
          {user === null ?
            <p>User not found.</p>
          :
            <>
              <Stack direction="horizontal" gap={4}>
                <Image src={user.avatar_url + '&s=32'} roundedCircle />
                <div>
                  <h1>{user.username}</h1>
                  {user.email && <h5>{user.email}</h5>}

                  {isFollower === true &&
                    <Button variant="primary" onClick={edit}>Edit</Button>
                  }
                </div>
              </Stack>
            </>
          }
        </>
      }
    </Body>
  );
}