import axios from 'axios';
import { IntegrationForm } from './integration-form';

const response = await axios.get("http://localhost:8000/testconnection");
console.log(response);

function App() {
  return (
    <div>
      <IntegrationForm />
    </div>
  );
}

export default App;
