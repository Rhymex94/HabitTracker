import axios from 'axios';

const api = axios.create({
  baseURL: '/api',  // Relative URL to use with Vite's proxy
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;