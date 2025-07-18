import type { NextPage } from 'next'
import React, { useState, useEffect } from 'react'
import Layout from '../components/layout'
import Message from '../components/message'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'


interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

const Home: NextPage = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'assistant', content: 'Hello! How can I help you with your PRD today?' },
  ]);
  const [input, setInput] = useState<string>('');
  const [mode, setMode] = useState<'generator' | 'reviewer'>('generator');
  const [approachType, setApproachType] = useState<'quick_fix' | 'generic'>('generic');
  const [loading, setLoading] = useState<boolean>(false);
  const [chatHistory, setChatHistory] = useState<string[]>(['Session 1', 'Session 2']); // Placeholder for chat history
  const [prdTemplateMarkdown, setPrdTemplateMarkdown] = useState<string>('');

  useEffect(() => {
    // Fetch PRD template markdown content
    fetch('/docs/prd_template.md')
      .then((response) => response.text())
      .then((text) => setPrdTemplateMarkdown(text))
      .catch((error) => console.error('Error fetching PRD template:', error));
  }, []);

  const handleSendMessage = async () => {
    if (input.trim() === '' || loading) return;

    const userMessage: ChatMessage = { role: 'user', content: input };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [...messages, userMessage],
          mode,
          approachType,
        }),
      });

      if (!response.body) {
        throw new Error("Response body is null");
      }

      let assistantResponse = '';
      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        assistantResponse += chunk;
        setMessages((prevMessages) => {
          const lastMessage = prevMessages[prevMessages.length - 1];
          if (lastMessage && lastMessage.role === 'assistant') {
            return [
              ...prevMessages.slice(0, -1),
              { ...lastMessage, content: assistantResponse },
            ];
          } else {
            return [...prevMessages, { role: 'assistant', content: assistantResponse }];
          }
        });
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages((prevMessages) => [
        ...prevMessages,
        { role: 'assistant', content: 'Error: Could not get a response.' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || loading) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Upload successful:', data);
      setMessages((prevMessages) => [
        ...prevMessages,
        { role: 'assistant', content: `Successfully uploaded and processed ${file.name}.` },
      ]);
    } catch (error) {
      console.error('Error uploading file:', error);
      setMessages((prevMessages) => [
        ...prevMessages,
        { role: 'assistant', content: `Error: Could not upload ${file.name}.` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout
      chatHistory={chatHistory}
      prdTemplateMarkdown={prdTemplateMarkdown}
    >
      <div className="flex flex-col h-full bg-gray-800 text-gray-100">
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg, index) => (
            <Message key={index} role={msg.role} content={msg.content} />
          ))}
        </div>
        <div className="p-4 border-t border-gray-700 flex flex-col space-y-4">
          <div className="flex items-center space-x-2">
            <Input
              type="text"
              placeholder="Type your message or upload a PRD..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleSendMessage();
                }
              }}
              className="flex-1 bg-gray-700 border-gray-600 text-gray-100 placeholder-gray-400"
              disabled={loading}
            />
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileUpload}
              className="hidden"
              id="pdf-upload"
              disabled={loading}
            />
            <label htmlFor="pdf-upload">
              <Button asChild disabled={loading}>
                <span>Upload PDF</span>
              </Button>
            </label>
            <Button onClick={handleSendMessage} disabled={loading}>
              Send
            </Button>
          </div>
          <div className="flex justify-center space-x-4">
            <div className="flex items-center space-x-2">
              <span className="text-gray-300">Type:</span>
              <Button
                onClick={() => setMode('generator')}
                variant={mode === 'generator' ? 'default' : 'outline'}
                disabled={messages.length > 1 || loading}
              >
                PRD Generate
              </Button>
              <Button
                onClick={() => setMode('reviewer')}
                variant={mode === 'reviewer' ? 'default' : 'outline'}
                disabled={messages.length > 1 || loading}
              >
                PRD Review
              </Button>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-gray-300">Mode:</span>
              <Button
                onClick={() => setApproachType('generic')}
                variant={approachType === 'generic' ? 'default' : 'outline'}
                disabled={messages.length > 1 || loading}
              >
                Generic
              </Button>
              <Button
                onClick={() => setApproachType('quick_fix')}
                variant={approachType === 'quick_fix' ? 'default' : 'outline'}
                disabled={messages.length > 1 || loading}
              >
                Quick Fix
              </Button>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Home;
