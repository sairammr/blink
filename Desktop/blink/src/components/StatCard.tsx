import { ReactNode } from 'react';
import { cn } from '../utils/cn';

interface StatCardProps {
  icon: ReactNode;
  title: string;
  value: string;
  className?: string;
  colorScheme: 'blue' | 'green' | 'purple' | 'orange';
}

const colorSchemes = {
  blue: {
    icon: 'bg-blue-100 dark:bg-blue-900 text-blue-500 dark:text-blue-300',
    text: 'bg-gradient-to-r from-blue-500 to-blue-600'
  },
  green: {
    icon: 'bg-green-100 dark:bg-green-900 text-green-500 dark:text-green-300',
    text: 'bg-gradient-to-r from-green-500 to-green-600'
  },
  purple: {
    icon: 'bg-purple-100 dark:bg-purple-900 text-purple-500 dark:text-purple-300',
    text: 'bg-gradient-to-r from-purple-500 to-purple-600'
  },
  orange: {
    icon: 'bg-orange-100 dark:bg-orange-900 text-orange-500 dark:text-orange-300',
    text: 'bg-gradient-to-r from-orange-500 to-orange-600'
  }
};

export function StatCard({ icon, title, value, className, colorScheme }: StatCardProps) {
  const colors = colorSchemes[colorScheme];
  
  return (
    <div className={cn(
      "bg-white dark:bg-gray-800 p-4 rounded-2xl shadow-lg transform hover:scale-105 transition-transform duration-300",
      className
    )}>
      <div className="flex items-center space-x-3">
        <div className={cn("p-2.5 rounded-xl", colors.icon)}>
          {icon}
        </div>
        <div>
          <h2 className="text-sm font-medium text-gray-600 dark:text-gray-300">{title}</h2>
          <p className={cn(
            "text-xl font-bold bg-clip-text text-transparent",
            colors.text
          )}>{value}</p>
        </div>
      </div>
    </div>
  );
}