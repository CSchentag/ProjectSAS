import { createContext, useContext, useCallback, useMemo } from 'react';
import SASApiClient from '../SASApiClient';
import { useFlash } from './FlashProvider';

const ApiContext = createContext();

export default function ApiProvider({ children }) {
  const flash = useFlash();

  const onError = useCallback(() => {
    flash('An unexpected error has occurred. Please try again later.', 'danger');
  }, [flash]);

  const api = useMemo(() => new SASApiClient(onError), [onError]);

  return (
    <ApiContext.Provider value={api}>
      {children}
    </ApiContext.Provider>
  );
}

export function useApi() {
  return useContext(ApiContext);
}