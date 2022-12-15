import { useState, useEffect } from 'react';
import Spinner from 'react-bootstrap/Spinner';
import Table from 'react-bootstrap/Table';
import { useApi } from '../contexts/ApiProvider';
import Accountant from './Accountant';
import BootstrapTable from 'react-bootstrap-table-next';
import filterFactory, { textFilter } from 'react-bootstrap-table2-filter';
import ToolkitProvider, {Search} from 'react-bootstrap-table2-toolkit/dist/react-bootstrap-table2-toolkit';

export default function Accountants() {
  const [accountants, setAccountants] = useState();
  const api = useApi();

  const { SearchBar, ClearSearchButton } = Search;

  const columns = [{
    dataField: 'name',
    text: 'Product Name',
  }, {
    dataField: 'email',
    text: 'Email',
  }, {
    dataField: 'phone_num',
    text: 'Phone Number',
  }, {
    dataField: 'company',
    text: 'Product Price',
  }, {
    dataField: 'specialty',
    text: 'Product Name',
  }, {
    dataField: 'about_me',
    text: 'Example',
  }];

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
              <ToolkitProvider
                keyField="id"
                data={ accountants }
                columns={ columns }
                search
              >
                {
                  props => (
                    <div>
                      <h3>Input something at below input field:</h3>
                      <SearchBar { ...props.searchProps } />
                      <ClearSearchButton { ...props.searchProps } />
                      <hr />
                      <BootstrapTable
                        { ...props.baseProps }
                      />
                    </div>
                  )
                }
              </ToolkitProvider>
              }
            </>
          }
        </>
      }
    </>
  );
}