import React, { useState, useEffect } from 'react';
import { Upload, Send, Settings, Loader } from 'lucide-react';
import axios from 'axios';

interface Message {
  id: number;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

interface Document {
  document_id: string;
  name: string;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "Upload a PDF document and I'll help you understand its content. You can ask me any questions about the document.",
      isUser: false,
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [currentDocument, setCurrentDocument] = useState<Document | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || !file.type.includes('pdf')) {
      setMessages(prev => [...prev, {
        id: Date.now(),
        text: "Please upload a PDF file.",
        isUser: false,
        timestamp: new Date()
      }]);
      return;
    }

    setIsLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/upload', formData);
      setCurrentDocument(response.data);
      setMessages(prev => [...prev, {
        id: Date.now(),
        text: `Successfully uploaded ${file.name}. What would you like to know about it?`,
        isUser: false,
        timestamp: new Date()
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        id: Date.now(),
        text: "Sorry, there was an error uploading the document. Please try again.",
        isUser: false,
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || !currentDocument) return;

    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/ask', {
        document_id: currentDocument.document_id,
        question: inputMessage
      });

      setMessages(prev => [...prev, {
        id: Date.now(),
        text: response.data.answer,
        isUser: false,
        timestamp: new Date()
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        id: Date.now(),
        text: "Sorry, I couldn't process your question. Please try again.",
        isUser: false,
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="flex justify-between items-center px-6 py-4 bg-white border-b">
        <div className="flex items-center space-x-3">
        {/* <div className="flex items-center space-x-2">
          <span className="font-semibold text-gray-800"></span>
        </div> */}
          <div className=" h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
          <img src="data:image/png;base64,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" alt="Logo" className="h-8" />            
          </div>
        </div>
        <div className="flex items-center space-x-4">
          <label className="flex items-center px-4 py-2 text-sm text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 cursor-pointer transition-colors">
            <Upload className="w-4 h-4 mr-2" />
            Upload PDF
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileUpload}
              className="hidden"
            />
          </label>
        </div>
      </header>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] p-4 rounded-2xl ${
                message.isUser
                  ? 'bg-indigo-600 text-white'
                  : 'bg-white text-gray-800 shadow-sm border border-gray-100'
              }`}
            >
              <p className="text-sm">{message.text}</p>
              <p
                className={`text-xs mt-2 ${
                  message.isUser ? 'text-indigo-200' : 'text-gray-400'
                }`}
              >
                {message.timestamp.toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Message Input */}
      <form onSubmit={handleSendMessage} className="p-4 bg-white border-t">
        <div className="flex items-center space-x-4 max-w-4xl mx-auto">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder={currentDocument ? "Ask a question about the document..." : "Upload a PDF to start asking questions"}
            disabled={!currentDocument || isLoading}
            className="flex-1 px-4 py-2 bg-gray-50 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <button
            type="submit"
            disabled={!currentDocument || !inputMessage.trim() || isLoading}
            className="p-2 text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <Loader className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
      </form>
    </div>
  );
}

export default App;