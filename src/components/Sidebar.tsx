import React from 'react';
import { Link } from 'react-router-dom';
import { FileText, Upload, Settings, HelpCircle, LogOut } from 'lucide-react';

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 bg-white border-r border-gray-200 h-full flex flex-col">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-xl font-bold flex items-center">
          <FileText className="mr-2 text-blue-600" />
          DocuQuery
        </h2>
      </div>
      <nav className="flex-1 overflow-y-auto py-4">
        <ul className="space-y-2 px-2">
          <li>
            <Link
              to="/"
              className="flex items-center px-4 py-2 text-gray-700 rounded-lg hover:bg-gray-100"
            >
              <Upload className="mr-3 text-gray-500" size={20} />
              Upload Document
            </Link>
          </li>
          <li>
            <Link
              to="/documents"
              className="flex items-center px-4 py-2 text-gray-700 rounded-lg hover:bg-gray-100"
            >
              <FileText className="mr-3 text-gray-500" size={20} />
              My Documents
            </Link>
          </li>
        </ul>
      </nav>
      <div className="p-4 border-t border-gray-200">
        <ul className="space-y-2">
          <li>
            <a
              href="#"
              className="flex items-center px-4 py-2 text-gray-700 rounded-lg hover:bg-gray-100"
            >
              <Settings className="mr-3 text-gray-500" size={20} />
              Settings
            </a>
          </li>
          <li>
            <a
              href="#"
              className="flex items-center px-4 py-2 text-gray-700 rounded-lg hover:bg-gray-100"
            >
              <HelpCircle className="mr-3 text-gray-500" size={20} />
              Help & Support
            </a>
          </li>
          <li>
            <a
              href="#"
              className="flex items-center px-4 py-2 text-gray-700 rounded-lg hover:bg-gray-100"
            >
              <LogOut className="mr-3 text-gray-500" size={20} />
              Logout
            </a>
          </li>
        </ul>
      </div>
    </aside>
  );
};