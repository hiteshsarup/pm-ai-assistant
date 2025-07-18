import React from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import HelpModal from './help-modal';

interface LayoutProps {
  children: React.ReactNode;
  chatHistory: string[];
  prdTemplateMarkdown: string;
}

const Layout: React.FC<LayoutProps> = ({
  children,
  chatHistory,
  prdTemplateMarkdown,
}) => {
  return (
    <div className="flex h-screen">
      {/* Left Pane */}
      <aside className="w-64 bg-gray-900 text-white p-4 flex flex-col border-r border-gray-700">
        <h2 className="text-lg font-semibold mb-4 text-gray-200">Chat History</h2>
        <div className="flex-1 overflow-y-auto space-y-2">
          {chatHistory.map((session, index) => (
            <div key={index} className="p-2 bg-gray-800 rounded-md text-gray-300 cursor-pointer hover:bg-gray-700">
              {session}
            </div>
          ))}
        </div>
        <div className="mt-4 pt-4 border-t border-gray-700">
          <HelpModal markdownContent={prdTemplateMarkdown} />
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex flex-col flex-1">
        {/* Top Bar (Simplified) */}
        <header className="bg-gray-900 p-4 border-b border-gray-700 flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-100">Shipsy PM Agent</h1>
        </header>

        {/* Main Pane (Chat Messages and new selectors) */}
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;