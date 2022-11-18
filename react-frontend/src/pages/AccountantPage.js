import { useState, useEffect } from 'react';
import Stack from 'react-bootstrap/Stack';
import Image from 'react-bootstrap/Image';
import Spinner from 'react-bootstrap/Spinner';
import { useParams } from 'react-router-dom';
import Body from '../components/Body';
import { useApi } from '../contexts/ApiProvider';

export default function AccountantPage() {
  const { username } = useParams();
  const [accountant, setAccountant] = useState();
  const api = useApi();

  useEffect(() => {
    (async () => {
      const response = await api.get('/accountants/' + username);
      setAccountant(response.ok ? response.body.data : null);
    })();
  }, [username, api]);

  return (
    <Body sidebar>
      {accountant === undefined ?
        <Spinner animation="border" />
      :
        <>
          {accountant === null ?
            <p>Accountant not found.</p>
          :
            <Stack direction="horizontal" gap={4}>
              <Image src={accountant.avatar + '&s=128'} roundedCircle />
              <div>
                <h1>{accountant.name}</h1>
                {accountant.about_me && <h5>{accountant.about_me}</h5>}
              </div>
            </Stack>
          }
        </>
      }
    </Body>
  );
}