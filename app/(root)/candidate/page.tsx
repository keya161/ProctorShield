
import React from 'react';
import ProctorControls from './ProctorControls';


const App: React.FC = () => {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Exam Proctoring System</h1>
      </header>
      <main>
        <ProctorControls />
      </main>
    </div>
  );
};

export default App;