import http from 'k6/http';
import { check, group, sleep } from 'k6';

const baseURL = "{{ api_url }}"
const accountNumbers = {{ account_numbers | to_json }}
const loginPath = '/api/signin';
const accountListPath = '/api/accounts';
const accountBalancePath = '/api/balance/';
const transferPath = '/api/transfer';
const accountTransactionsPath = '/api/transactions/';

const headers = {
  'Content-Type': 'application/json',
};

function getRandomUsername() {
  const randomNum = Math.floor(Math.random() * 1000) + 1;
  return `${randomNum}@ubu.ac.th`;
}

function getRandomAccountNumber(ownAcc) {
  let randAcc = accountNumbers[Math.floor(Math.random() * accountNumbers.length)];
  while (randAcc == ownAcc) {
    randAcc = accountNumbers[Math.floor(Math.random() * accountNumbers.length)];
  }
  return randAcc;
}

export default function () {
  group('Authentication', function () {
    const loginPayload = {
      grant_type: 'password',
      username: getRandomUsername(),
      password: 'test',
    };

    const loginRes = http.post(`${baseURL}${loginPath}`, loginPayload);
    check(loginRes, {
      'Login status is 200': (res) => res.status === 200,
      'Access token is present': (res) => !!res.json('access_token'),
    });

    const accessToken = loginRes.json('access_token');
    headers['Authorization'] = `Bearer ${accessToken}`;
  });

  group('API Tests', function () {
    const accountListRes = http.get(`${baseURL}${accountListPath}`, { headers: headers });
    check(accountListRes, {
      'Account list status is 200': (res) => res.status === 200,
      'Account list response has data': (res) => !!res.json(),
    });

    const accounts = accountListRes.json();
    const accountBalanceRes = http.get(`${baseURL}${accountBalancePath}${accounts[0].account_number}`, { headers: headers });
    check(accountBalanceRes, {
      'Account balance status is 200': (res) => res.status === 200,
      'Account balance response has data': (res) => !!res.json(),
    });

    const transferPayload = {
      fromacc: accounts[0].account_number,
      toacc: getRandomAccountNumber(accounts[0].account_number),
      amount: Math.floor(Math.random() * (5000 - 100 + 1) + 100),
    };

    const transferRes = http.post(`${baseURL}${transferPath}`, JSON.stringify(transferPayload), { headers: headers });
    check(transferRes, {
      'Transfer status is 200': (res) => res.status === 200,
      'Transfer response has data': (res) => !!res.json(),
    });

    const accountTransactionsRes = http.get(`${baseURL}${accountTransactionsPath}${accounts[0].account_number}`, { headers: headers });
    check(accountTransactionsRes, {
      'Account transactions status is 200': (res) => res.status === 200,
      'Account transactions response has data': (res) => !!res.json(),
    });
  });

  // sleep(1);
}
