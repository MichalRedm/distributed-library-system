import "./App.scss";
import User from "./components/User";
import UserList from "./components/UserList";

function App() {
  return (
    <div className="App">
      <UserList />
      <User />
    </div>
  );
}

export default App;
