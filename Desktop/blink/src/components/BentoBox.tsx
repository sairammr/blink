// import React from 'react';
import {  User, Clock } from 'lucide-react';
import { BlinkStats } from '../types';
// import { BlinkGraph } from './BlinkGraph'; // Added import

interface BentoBoxProps {
  username: string;
  stats: BlinkStats;
}

export function BentoBox({ username, stats }: BentoBoxProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4 p-4 max-w-7xl mx-auto">
      {/* Username Box */}
      <div className="md:col-span-2 bg-gradient-to-br from-blue-500 to-blue-600 p-6 rounded-2xl shadow-lg text-white transform hover:scale-[1.02] transition-all duration-300">
        <div className="flex items-center space-x-3">
          <div className="p-3 bg-white/20 rounded-xl backdrop-blur-sm">
            <User className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-sm font-medium opacity-90">Welcome</h2>
            <p className="text-2xl font-bold">{username}</p>
          </div>
        </div>
      </div>

      {/* Today's Blink Count */}
      {/* <div className="md:col-span-2 bg-gradient-to-br from-green-500 to-emerald-600 p-6 rounded-2xl shadow-lg text-white transform hover:scale-[1.02] transition-all duration-300">
        <div className="flex items-center space-x-3">
          <div className="p-3 bg-white/20 rounded-xl backdrop-blur-sm">
            <Timer className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-sm font-medium opacity-90">Today's Blinks</h2>
            <p className="text-3xl font-bold">{stats.todayCount}</p>
          </div>
        </div>
      </div> */}

      {/* 20 Min Average */}
      <div className="bg-gradient-to-br md:col-span-2 from-purple-500 to-purple-600 p-6 rounded-2xl shadow-lg text-white transform hover:scale-[1.02] transition-all duration-300">
        <div className="flex items-center space-x-3">
          <div className="p-3 bg-white/20 rounded-xl backdrop-blur-sm">
            <Clock className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-sm font-medium opacity-90">20min Avg</h2>
            <p className="text-2xl font-bold">{stats.twentyMinAvg}</p>
          </div>
        </div>
      </div>

      {/* 1 Hour Average */}
      <div className="bg-gradient-to-br md:col-span-2 from-orange-500 to-red-600 p-6 rounded-2xl shadow-lg text-white transform hover:scale-[1.02] transition-all duration-300">
        <div className="flex items-center space-x-3">
          <div className="p-3 bg-white/20 rounded-xl backdrop-blur-sm">
            <Clock className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-sm font-medium opacity-90">1hr Avg</h2>
            <p className="text-2xl font-bold">{stats.hourlyAvg}</p>
          </div>
        </div>
      </div>

      {/* Graph Box */}
      {/* <div className="md:col-span-4 bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-lg">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-xl">
              <LineChart className="w-6 h-6 text-blue-500 dark:text-blue-300" />
            </div>
            <h2 className="text-lg font-semibold text-gray-700 dark:text-gray-300">Blink Analytics</h2>
          </div>
          <select className="bg-gray-100 dark:bg-gray-700 rounded-xl px-4 py-2 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="daily">Today</option>
            <option value="weekly">This Week</option>
            <option value="monthly">This Month</option>
          </select>
        </div>
        <BlinkGraph />
      </div> */}
    </div>
  );
}