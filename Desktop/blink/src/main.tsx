import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './App';  // Updated import to use named export
import './index.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>
);