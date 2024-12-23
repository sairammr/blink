import React from 'react';
import { Moon, Sun, LogOut, Settings as SettingsIcon } from 'lucide-react';

interface SettingsProps {
  isDark: boolean;
  onThemeToggle: () => void;
  onLogout: () => void;
}

export function Settings({ isDark, onThemeToggle, onLogout }: SettingsProps) {
  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-lg">
      <div className="flex items-center space-x-3 mb-6">
        <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-xl">
          <SettingsIcon className="w-6 h-6 text-blue-500 dark:text-blue-300" />
        </div>
        <h2 className="text-lg font-semibold text-gray-600 dark:text-gray-300">Settings</h2>
      </div>

      <div className="space-y-4">
        <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
          <span className="text-sm font-medium">Theme</span>
          <button
            onClick={onThemeToggle}
            className="p-3 rounded-xl bg-white dark:bg-gray-600 hover:bg-gray-100 dark:hover:bg-gray-500 transition-colors shadow-md"
          >
            {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </button>
        </div>

        <button
          onClick={onLogout}
          className="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-gradient-to-r from-red-500 to-pink-500 hover:from-red-600 hover:to-pink-600 text-white rounded-xl transition-colors shadow-md"
        >
          <LogOut className="w-5 h-5" />
          <span>Logout</span>
        </button>
      </div>
    </div>
  );
}