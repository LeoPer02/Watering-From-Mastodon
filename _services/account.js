import { fetchWrapper } from './fetchWrapper';
import { BehaviorSubject } from 'rxjs';

const userSubject = new BehaviorSubject(null);
const apiUrl = 'http://172.18.0.1:5000';
const baseUrl = `${apiUrl}`;
const apiToken =
  '3';
const userToken =
  '3';

export const accountService = {
  login,
  logout,
  register, // Post/ user, pass
  control_agents, // Get vai ser as plantinhas
  add_ca, // Post
  remove_ca, // Post
  get_threshold,
  set_thresholds,
  commands, //GET É um /id
  action, // Get com um id/command
  pool, // Get  
  user: userSubject.asObservable(),
  get userValue() {
    return userSubject.value;
  },
};

function login(username, password) {
  const params = { username, password };
  return fetchWrapper.post(`${baseUrl}/login`, params)
    .then(user => {
      console.log('Login Response:', user); // Log the response
      userSubject.next(user);
      startRefreshTokenTimer();
      return user;
    })
    .catch(error => {
      console.error('Login Error:', error); // Log any errors
    });
}

function logout() {
  fetchWrapper.post(`${baseUrl}/logout`, {}).then(() => {
    stopRefreshTokenTimer();
    userSubject.next(null);
  });
}

function register(username, password) {
  const params = { username, password };
  console.log(params);
  return fetchWrapper.post(`${baseUrl}/register`, params);
}

function control_agents() {
  return fetchWrapper.get(`${baseUrl}/control_agents`);
}

function add_ca(control_agent_name, control_agent_ip, control_agent_port) {
  const params = { control_agent_name, control_agent_ip, control_agent_port };
  return fetchWrapper.post(`${baseUrl}/add_ca`, params);
}

function remove_ca(control_agent_ip, control_agent_port) {
  const params = { control_agent_ip, control_agent_port };
  return fetchWrapper.post(`${baseUrl}/remove_ca`, params);
}

function commands(ca_id) {
  return fetchWrapper.get(`${baseUrl}/commands/${ca_id}`);
}

function action(ca_id, command) {
  return fetchWrapper.get(`${baseUrl}/action/${ca_id}/${command}`);
}

function get_threshold(ca_id) {
  return fetchWrapper.get(`${baseUrl}/thresholds/${ca_id}`);
}

function set_thresholds(params) {
  return fetchWrapper.post(`${baseUrl}/set_thresholds`, params);
}

function pool() {
  return fetchWrapper.get(`${baseUrl}/test/pool`);
}

// Helper functions for managing token refresh
function refreshToken() {
  // Implement token refresh logic if necessary
}

let refreshTokenTimeout;

function startRefreshTokenTimer() {
  // Implement timer logic if necessary
}

function stopRefreshTokenTimer() {
  clearTimeout(refreshTokenTimeout);
}