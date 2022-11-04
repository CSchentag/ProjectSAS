import { useState, useEffect } from 'react';
import Stack from 'react-bootstrap/Stack';
import Image from 'react-bootstrap/Image';
import Spinner from 'react-bootstrap/Spinner';
import { useParams } from 'react-router-dom';
import Body from '../components/Body';
import { useApi } from '../contexts/ApiProvider';

export default function UserPage() {
  const { username } = useParams();
  const [user, setUser] = useState();
  const api = useApi();

  useEffect(() => {
    (async () => {
      const response = await api.get('/accountants/' + username);
      setUser(response.ok ? response.body.data : null);
    })();
  }, [username, api]);

  return (
    <Body sidebar>
      {user === undefined ?
        <Spinner animation="border" />
      :
        <>
          {user === null ?
            <p>User not found.</p>
          :
            <Stack direction="horizontal" gap={4}>
              <Image src={user.avatar + '&s=128'} roundedCircle />
              <div>
                <h1>{user.name}</h1>
                {user.about_me && <h5>{user.about_me}</h5>}
              </div>
            </Stack>
          }
        </>
      }
    </Body>
  );
}