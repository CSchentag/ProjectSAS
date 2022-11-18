import { useState, useEffect } from 'react';
import Spinner from 'react-bootstrap/Spinner';
import { useApi } from '../contexts/ApiProvider';
import Accountant from './Accountant';

export default function Accountants() {
  const [accountants, setAccountants] = useState();
  const api = useApi();

  useEffect(() => {
    (async () => {
      const response = await api.get('/accountants/');
      if (response.ok) {
        setAccountants(response.body.data);
      }
      else {
        setAccountants(null);
      }
    })();
  }, [api]);

  return (
    <>
      {accountants === undefined ?
        <Spinner animation="border" />
      :
        <>
          {accountants === null ?
             <p>Could not retrieve accountant data.</p>
          :
            <>
              {accountants.length === 0 ?
                <p>No accountants found in database.</p>
              :
                accountants.map(accountant => <Accountant key={accountant.id} accountant={accountant} />)
              }
            </>
          }
        </>
      }
    </>
  );
}