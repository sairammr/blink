import React, { useState, useEffect } from 'react';

export function BlinkGraph() {
  const [data, setData] = useState<{ hour: number; value: number }[]>([]);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    // Generate mock data
    const newData = Array.from({ length: 24 }, (_, i) => ({
      hour: i,
      value: Math.floor(Math.random() * 50) + 10
    }));
    setData(newData);
    setIsAnimating(true);
  }, []);

  const maxValue = Math.max(...data.map(d => d.value));
  
  return (
    <div className="relative h-64">
      {/* Y-axis labels */}
      <div className="absolute left-0 top-0 h-full flex flex-col justify-between text-xs text-gray-500 dark:text-gray-400 pr-2">
        <span>{maxValue}</span>
        <span>{Math.floor(maxValue / 2)}</span>
        <span>0</span>
      </div>

      {/* Graph */}
      <div className="ml-8 h-full flex items-end space-x-1">
        {data.map((item, index) => (
          <div
            key={item.hour}
            className="flex-1 flex flex-col items-center group"
          >
            <div className="w-full relative">
              <div
                style={{
                  height: isAnimating ? `${(item.value / maxValue) * 100}%` : '0%',
                  transitionDelay: `${index * 50}ms`
                }}
                className="bg-gradient-to-t from-blue-500 to-purple-500 rounded-t-lg transition-all duration-700 ease-out group-hover:from-blue-600 group-hover:to-purple-600"
              >
                {/* Tooltip */}
                <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white px-2 py-1 rounded text-xs opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                  {item.value} blinks
                </div>
              </div>
            </div>
            <span className="text-xs mt-1 text-gray-500 dark:text-gray-400">
              {item.hour}h
            </span>
          </div>
        ))}
      </div>

      {/* Grid lines */}
      <div className="absolute inset-y-0 left-8 right-0 flex flex-col justify-between pointer-events-none">
        {[...Array(5)].map((_, i) => (
          <div
            key={i}
            className="border-t border-gray-200 dark:border-gray-700 w-full"
          />
        ))}
      </div>
    </div>
  );
}