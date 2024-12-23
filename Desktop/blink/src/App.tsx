import React, { useState, useEffect } from 'react';
import { BentoBox } from './components/BentoBox';
import { CameraPreview } from './components/CameraPreview';
import { Settings } from './components/Settings';
import { BlinkStats } from './types';

export function App() {  // Changed to named export
  const [isDark, setIsDark] = useState(false);
  const [stats, setStats] = useState<BlinkStats>({
    todayCount: 0,
    twentyMinAvg: 0,
    hourlyAvg: 0
  });

  useEffect(() => {
    const interval = setInterval(() => {
      setStats(prev => ({
        todayCount: prev.todayCount + Math.floor(Math.random() * 3),
        twentyMinAvg: Math.floor(Math.random() * 20),
        hourlyAvg: Math.floor(Math.random() * 15)
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);

  const handleLogout = () => {
    console.log('Logging out...');
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white transition-colors p-4">
      <div className="max-w-7xl mx-auto space-y-4">
        <BentoBox username="John Doe" stats={stats} />
        <div className="md:col-span-2">
            <CameraPreview />
          </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          
          <div>
            <Settings 
              isDark={isDark}
              onThemeToggle={() => setIsDark(!isDark)}
              onLogout={handleLogout}
            />
          </div>
        </div>
      </div>
    </div>
  );
}