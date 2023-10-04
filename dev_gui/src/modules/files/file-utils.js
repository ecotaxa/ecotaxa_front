import {
  v5 as uuidv5
} from 'uuid';
const NAMESPACE = '1b671a64-80d5-498e-99b0-ea01ff1f3341';

function generate_uuid(name, namespace = NAMESPACE) {
  return uuidv5(name, namespace);
}
export {
  generate_uuid
}