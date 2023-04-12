import http from 'k6/http';
import { sleep } from 'k6';

export default function() {
  let apiurl = __ENV.API_URL;
  let response = http.get(`${apiurl}/api/docs`);
  sleep(1);
}
