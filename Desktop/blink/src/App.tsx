import React, { useState, useEffect } from 'react';
import { BentoBox } from './components/BentoBox';
import { CameraPreview } from './components/CameraPreview';
import { Settings } from './components/Settings';
import { BlinkStats } from './types';
import { invoke } from '@tauri-apps/api/core';

export function App() {  // Changed to named export
  const [isDark, setIsDark] = useState(false);
  const [stats, setStats] = useState<BlinkStats>({
    todayCount: 0,
    twentyMinAvg: 0,
    hourlyAvg: 0
  });

  const [blinkData, setBlinkData] = useState<{ start_time: string, end_time: string, avg_value: number }[]>([]);

  useEffect(() => {
    const interval = setInterval(() => {
      const fetchBlinkData = async () => {
        try {
          const data = await invoke('get_avg');
          const parsedData = JSON.parse(data as string);
          setBlinkData(parsedData);
        } catch (error) {
          console.error('Error fetching blink data:', error);
        }
      };

      fetchBlinkData();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (blinkData.length > 0) {
      const todayCount = blinkData.reduce((acc, value) => acc + value.avg_value, 0);  // Total blinks for today
      const twentyMinAvg = blinkData[blinkData.length - 1].avg_value;  // Last entry for 20 min average

      const lastThreeBlinks = blinkData.slice(-3);
      const hourlyAvg = lastThreeBlinks.length > 0 ? lastThreeBlinks.reduce((acc, value) => acc + value.avg_value, 0) / lastThreeBlinks.length : 0;  // Average of the last 3 values

      setStats({
        todayCount,
        twentyMinAvg,
        hourlyAvg,
      });
    }
  }, [blinkData]);

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
