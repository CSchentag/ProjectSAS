import { useState, useEffect } from 'react';
import Spinner from 'react-bootstrap/Spinner';
import Table from 'react-bootstrap/Table';
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
              <Table striped bordered hover>
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Phone Number</th>
                    <th>Company</th>
                    <th>Specialty</th>
                    <th>About Me</th>
                  </tr>
                </thead>
                <tbody>
                  {accountants && Object.keys(accountants).map((keyName, keyIndex) => 
                      <tr key={keyIndex}>
                          <td>{(accountants[keyName].name)}</td>
                          <td>{(accountants[keyName].email)}</td>
                          <td>{(accountants[keyName].phone_num)}</td>
                          <td>{(accountants[keyName].company)}</td>
                          <td>{(accountants[keyName].specialty)}</td>
                          <td>{(accountants[keyName].about_me)}</td>
                   </tr>)}
                </tbody>
              </Table>
              }
            </>
          }
        </>
      }
    </>
  );
}