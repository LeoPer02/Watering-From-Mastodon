import { accountService } from '../_services/account';
import Toast from 'react-native-toast-message';

export const fetchWrapper = {
  get,
  post,
  put,
  delete: _delete,
};

function get(url) {
  const requestOptions = {
    method: 'GET',
    headers: authHeader(url),
    credentials: 'include'
  };
  return fetch(url, requestOptions).then(handleResponse);
}

function post(url, body, useFormData = true) {
  const headers = { ...authHeader(url) };
  let bodyToSend;

  if (useFormData) {
      // Use FormData to send data as form fields
      const formData = new FormData();
      for (const key in body) {
          formData.append(key, body[key]);
      }
      bodyToSend = formData;
      // Content-Type is set automatically by the browser for FormData
  } else {
      // Use JSON to send data
      headers['Content-Type'] = 'application/json';
  }

  const requestOptions = {
      method: 'POST',
      headers: headers,
      credentials: 'include',
      body: bodyToSend
  };
  return fetch(url, requestOptions).then(handleResponse);
}

function put(url, body) {
  const requestOptions = {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...authHeader(url) },
    body: JSON.stringify(body),
    credentials: 'include'
  };
  return fetch(url, requestOptions).then(handleResponse);
}

// prefixed with underscored because delete is a reserved word in javascript
function _delete(url) {
  const requestOptions = {
    method: 'DELETE',
    headers: authHeader(url),
    credentials: 'include'
  };
  return fetch(url, requestOptions).then(handleResponse);
}

// helper functions

function authHeader(url) {
  /*
    // return auth header with jwt if user is logged in and request is to the api url
    const apiUrl = '/api/'; // TODO
    const user = accountService.userValue;
    const isLoggedIn = user && user.jwtToken;
    // Checking whether '/api/' is included should be fine for now
    const isApiUrl = url.includes(apiUrl);
    if (isLoggedIn && isApiUrl) {
        return { Authorization: `Bearer ${user.jwtToken}` };
    } else {
        return {};
    }
    */
}

function handleResponse(response) {
  //console.log(response);

  const rateLimitRemaining = response.headers.get('x-ratelimit-remaining');
  
  if (rateLimitRemaining === '0') {
    return ;
  }

  return response.text().then((text) => {
    //console.log(text);
    const data = text && JSON.parse(text)

    if (!response.ok) {
      if ([401, 403].includes(response.status) && accountService.userValue) {
        // auto logout if 401 Unauthorized or 403 Forbidden response returned from api
        accountService.logout();
      }

      const error = (data && data.message) || response.statusText;
      return Promise.reject(error);
    }

    return data;
  });
}
