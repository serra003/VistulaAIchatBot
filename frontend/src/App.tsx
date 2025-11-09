import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import logo from './assets/image 1.png';
import logo1 from './assets/logoITCLUB 1.png';

interface Message {
  sender: 'user' | 'ai';
  text: string;
}

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (text?: string) => {
    const userInput = text || input;
    if (!userInput) return;

    setMessages([...messages, { sender: 'user', text: userInput }]);
    setInput('');

    try {
      const response = await axios.post('http://localhost:8000/ask', {
        question: userInput,
      });
      const answer = response.data.answer;
      setMessages(prev => [...prev, { sender: 'ai', text: answer }]);
    } catch (error) {
      console.error('Error connecting to backend:', error);
      setMessages(prev => [
        ...prev,
        { sender: 'ai', text: 'Sorry, backend is not responding.' },
      ]);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') sendMessage();
  };

  return (
    <div className="App">
      {/* TOP BAR */}
      <div className="top">
        <img src={logo} alt="Logo" />
        <span className="heading">
          Vistula Academy of Finance<br />
          and Business
        </span>
        <img src={logo1} alt="Logo" />
      </div>

      {/* MAIN CONTENT */}
      <div className="main">
        <div className="title-container">
          <h1 className="title">Hi! I'm VistulaBot!</h1>
          <p className="subtitle">How can I help you today?</p>
        </div>

        {/* CHAT BOX */}
        <div
          style={{
            backgroundColor: '#addaf8ff',
            borderRadius: '12px',
            padding: '20px',
            width: '100%',  
            maxWidth: '600px',
            height: '300px',
            overflowY: 'auto',
            marginBottom: '15px',
          }}
        >
          {messages.map((msg, index) => (
            <div
              key={index}
              style={{
                textAlign: msg.sender === 'user' ? 'right' : 'left',
                margin: '8px 0',
              }}
            >
             <div
            style={{
            display: 'inline-block',
            backgroundColor: msg.sender === 'user' ? '#5AA0E0' : '#E3F2FD',
            color: '#0A2740',
            padding: '10px 15px',
            borderRadius: '18px',
            maxWidth: '80%',
            wordWrap: 'break-word',
  }}
              >
                {msg.text}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef}></div>
        </div>

        {/* INPUT + BUTTON */}
        <div className="search">
          <input
            type="text"
            placeholder="Ask Me Anything :)"
            className="search-input"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
          />
          <button className="arrow" onClick={() => sendMessage()}>
            <svg
              width="20"
              height="20"
              viewBox="0 0 20 20"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M10 4L10 16M10 4L4 10M10 4L16 10"
                stroke="white"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
        </div>

        {/* QUICK BUTTONS */}
        <div className="buttons">
          <button onClick={() => sendMessage('How can I get my student ID?')}>
            How can I get My student ID?
          </button>
          <button onClick={() => sendMessage('Where can I submit my documents?')}>
            Where Can I submit my documents?
          </button>
        </div>
      </div>
    </div>
  );
};

export default App;  