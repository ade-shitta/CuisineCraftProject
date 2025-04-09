import axios from 'axios';
import Cookies from 'js-cookie';

const CSRF_COOKIE_NAME = 'csrftoken';
const CSRF_HEADER_NAME = 'X-CSRFToken';

export const getCSRFToken = (): string => {
  return Cookies.get(CSRF_COOKIE_NAME) || '';
};

export const fetchCSRFToken = async (): Promise<string> => {
  try {
    await axios.get('http://localhost:8000/api/csrf/', { withCredentials: true });
    return getCSRFToken();
  } catch (error) {
    console.error('Error fetching CSRF token', error);
    return '';
  }
};

export const setCSRFTokenHeader = (config: any): any => {
  const token = getCSRFToken();
  if (token && config.method !== 'get' && config.method !== 'GET') {
    config.headers[CSRF_HEADER_NAME] = token;
  }
  return config;
};