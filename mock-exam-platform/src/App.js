import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import SubjectSelection from './components/SubjectSelection';
import TestPage from './components/TestPage';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/exam/:examId" element={<SubjectSelection />} />
          <Route path="/test/:examId/:subjectId" element={<TestPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
