import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import reportWebVitals from './reportWebVitals';

const root = ReactDOM.createRoot(document.getElementById('reactFrontendContainer'));
root.render(
  <React.StrictMode>
    <App
      notify={false}
      appTheme={window.appTheme.toString().toLowerCase() || "dark"}
      appEnv={window.appEnv.toString().toLowerCase() || "prod"}
      appSinhala={Boolean(window.appSinhala) || true}
    />
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
