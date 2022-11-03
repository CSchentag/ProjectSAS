

import { createContext, useContext } from 'react';
import SASApiClient from '../SASApiClient';

const ApiContext = createContext();

export default function ApiProvider({ children }) {
  const api = new SASApiClient();

  return (
    <ApiContext.Provider value={api}>
      {children}
    </ApiContext.Provider>
  );
}

export function useApi() {
  return useContext(ApiContext);
}