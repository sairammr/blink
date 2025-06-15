import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer } from 'recharts';
import { Calendar, Eye, HelpCircle, TrendingUp } from 'lucide-react';

// Mock data for the blink rate chart
const generateBlinkRateData = () => {
  const data = [];
  const times = [
    '00:30', '01:25', '02:20', '03:20', '04:20', '05:20', '06:20', '07:20', '08:20', '09:20',
    '10:15', '11:05', '11:55', '12:50', '13:45', '14:40', '15:35', '16:30', '17:25', '18:20',
    '19:10', '20:05', '21:00', '21:55', '22:55', '23:55'
  ];
  
  times.forEach(time => {
    data.push({
      time,
      blinks: Math.floor(Math.random() * 14) + 7 // Random blinks between 7-21
    });
  });
  
  return data;
};

// Mock data for recent activity
const generateRecentActivity = () => {
  const activities = [];
  const baseTime = new Date();
  baseTime.setHours(23, 55, 0, 0);
  
  const times = [
    '22:20', '22:25', '22:30', '22:35', '22:40', '22:45', '22:50', '22:55', '23:00', '23:05',
    '23:10', '23:15', '23:20', '23:25', '23:30', '23:35', '23:40', '23:45', '23:50', '23:55'
  ];
  
  const blinkCounts = [20, 21, 22, 24, 23, 25, 18, 20, 26, 20, 24, 20, 19, 22, 19, 16, 24, 21, 21, 20];
  
  times.forEach((time, index) => {
    activities.push({
      time,
      blinks: blinkCounts[index] || Math.floor(Math.random() * 10) + 16
    });
  });
  
  return activities;
};

const BlinkAnalyticsDashboard = () => {
  const [blinkRateData, setBlinkRateData] = useState([]);
  const [recentActivity, setRecentActivity] = useState([]);
  const [currentStats, setCurrentStats] = useState({
    averageBlinks: 17.0,
    last20Minutes: 21.5,
    totalToday: 24580,
    percentageAbove: 26.2
  });

  // Mock function to simulate real-time updates
  const updateStats = () => {
    setCurrentStats(prev => ({
      ...prev,
      last20Minutes: prev.last20Minutes + (Math.random() - 0.5) * 2,
      totalToday: prev.totalToday + Math.floor(Math.random() * 10),
      percentageAbove: prev.percentageAbove + (Math.random() - 0.5) * 5
    }));
  };

  useEffect(() => {
    setBlinkRateData(generateBlinkRateData());
    setRecentActivity(generateRecentActivity());
    
    // Update stats every 30 seconds
    const interval = setInterval(updateStats, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const styles = {
    container: {
      minHeight: '100vh',
      backgroundColor: 'white',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    },
    header: {
      backgroundColor: 'white',
      borderBottom: '1px solid #f3f4f6',
      padding: '0 24px'
    },
    headerContent: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      height: '56px'
    },
    headerLeft: {
      display: 'flex',
      alignItems: 'center',
      gap: '12px'
    },
    logo: {
      width: '24px',
      height: '24px',
      backgroundColor: 'black',
      borderRadius: '50%',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    },
    logoText: {
      fontSize: '16px',
      fontWeight: '500',
      color: '#111827'
    },
    headerRight: {
      fontSize: '14px',
      color: '#6b7280',
      display: 'flex',
      alignItems: 'center',
      gap: '8px'
    },
    main: {
      padding: '24px'
    },
    pageHeader: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      marginBottom: '24px'
    },
    pageTitle: {
      fontSize: '24px',
      fontWeight: '600',
      color: '#111827',
      margin: 0
    },
    dateInfo: {
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      fontSize: '14px',
      color: '#9ca3af'
    },
    tabs: {
      display: 'flex',
      gap: '32px',
      marginBottom: '32px'
    },
    tab: {
      fontSize: '14px',
      color: '#6b7280',
      backgroundColor: 'transparent',
      border: 'none',
      cursor: 'pointer',
      padding: '8px 0',
      borderBottom: '2px solid transparent'
    },
    activeTab: {
      color: '#111827',
      fontWeight: '500'
    },
    statsGrid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(3, 1fr)',
      gap: '24px',
      marginBottom: '32px'
    },
    statsCard: {
      backgroundColor: 'white',
      border: '1px solid #e5e7eb',
      borderRadius: '8px',
      padding: '24px'
    },
    statsHeader: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      marginBottom: '12px'
    },
    statsTitle: {
      fontSize: '14px',
      color: '#6b7280',
      margin: 0
    },
    statsValue: {
      fontSize: '24px',
      fontWeight: '600',
      color: '#111827',
      margin: '4px 0'
    },
    statsSubtext: {
      fontSize: '12px',
      color: '#9ca3af',
      margin: 0
    },
    chartsGrid: {
      display: 'grid',
      gridTemplateColumns: '2fr 1fr',
      gap: '24px'
    },
    chartCard: {
      backgroundColor: 'white',
      border: '1px solid #e5e7eb',
      borderRadius: '8px',
      padding: '24px'
    },
    chartHeader: {
      marginBottom: '24px'
    },
    chartTitle: {
      fontSize: '18px',
      fontWeight: '500',
      color: '#111827',
      margin: '0 0 16px 0'
    },
    chartTabs: {
      display: 'flex',
      gap: '24px',
      fontSize: '14px',
      borderBottom: '1px solid #f3f4f6',
      paddingBottom: '8px'
    },
    chartTab: {
      backgroundColor: 'transparent',
      border: 'none',
      cursor: 'pointer',
      padding: '8px 0',
      borderBottom: '1px solid transparent'
    },
    activeChartTab: {
      color: '#111827',
      fontWeight: '500',
      borderBottom: '1px solid #111827'
    },
    inactiveChartTab: {
      color: '#9ca3af'
    },
    chartContainer: {
      height: '320px'
    },
    activityCard: {
      backgroundColor: 'white',
      border: '1px solid #e5e7eb',
      borderRadius: '8px',
      padding: '24px'
    },
    activityHeader: {
      marginBottom: '24px'
    },
    activityTitle: {
      fontSize: '18px',
      fontWeight: '500',
      color: '#111827',
      margin: '0 0 4px 0'
    },
    activitySubtitle: {
      fontSize: '14px',
      color: '#9ca3af',
      margin: 0
    },
    activityList: {
      display: 'flex',
      flexDirection: 'column',
      gap: '12px'
    },
    activityItem: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between'
    },
    activityItemLeft: {
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
      flex: 1
    },
    activityTime: {
      fontSize: '12px',
      color: '#9ca3af',
      width: '32px'
    },
    activityBar: {
      flex: 1,
      backgroundColor: '#e5e7eb',
      height: '16px',
      borderRadius: '2px',
      overflow: 'hidden'
    },
    activityBarFill: {
      backgroundColor: 'black',
      height: '16px',
      borderRadius: '2px'
    },
    activityCount: {
      fontSize: '12px',
      color: '#374151',
      width: '24px',
      textAlign: 'right',
      marginLeft: '8px'
    }
  };

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <div style={styles.headerContent}>
          <div style={styles.headerLeft}>
            <div style={styles.logo}>
              <Eye size={12} color="white" />
            </div>
            <span style={styles.logoText}>Blink Analytics</span>
          </div>
          <div style={styles.headerRight}>
            Data Analyst Dashboard
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div style={styles.main}>
        {/* Page Header */}
        <div style={styles.pageHeader}>
          <h1 style={styles.pageTitle}>Blink Data Analysis</h1>
          <div style={styles.dateInfo}>
            <Calendar size={16} />
            <span>15/06/2025</span>
          </div>
        </div>
        {/* Stats Cards */}
        <div style={styles.statsGrid}>
          <div style={styles.statsCard}>
            <div style={styles.statsHeader}>
              <h3 style={styles.statsTitle}>Average Blink Count</h3>
              <HelpCircle size={16} color="#d1d5db" />
            </div>
            <div style={styles.statsValue}>
              {currentStats.averageBlinks.toFixed(1)} blinks/min
            </div>
            <p style={styles.statsSubtext}>Overall average</p>
          </div>

          <div style={styles.statsCard}>
            <div style={styles.statsHeader}>
              <h3 style={styles.statsTitle}>Last 20 Minutes</h3>
              <HelpCircle size={16} color="#d1d5db" />
            </div>
            <div style={styles.statsValue}>
              {currentStats.last20Minutes.toFixed(1)} blinks/min
            </div>
            <p style={styles.statsSubtext}>
              +{Math.abs(currentStats.percentageAbove).toFixed(1)}% above average
            </p>
          </div>

          <div style={styles.statsCard}>
            <div style={styles.statsHeader}>
              <h3 style={styles.statsTitle}>Total Blinks Today</h3>
              <TrendingUp size={16} color="#d1d5db" />
            </div>
            <div style={styles.statsValue}>
              {currentStats.totalToday.toLocaleString()}
            </div>
            <p style={styles.statsSubtext}>Updated just now</p>
          </div>
        </div>

        {/* Charts Section */}
        <div style={styles.chartsGrid}>
          {/* Blink Rate Chart */}
          <div style={styles.chartCard}>
            <div style={styles.chartHeader}>
              <h2 style={styles.chartTitle}>Blink Rate Over Time</h2>
              <div style={styles.chartTabs}>
                <button style={{...styles.chartTab, ...styles.activeChartTab}}>Day</button>
                <button style={{...styles.chartTab, ...styles.inactiveChartTab}}>Week</button>
                <button style={{...styles.chartTab, ...styles.inactiveChartTab}}>Month</button>
              </div>
            </div>
            <div style={styles.chartContainer}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={blinkRateData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                  <XAxis 
                    dataKey="time" 
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 11, fill: '#9CA3AF' }}
                    interval="preserveStart"
                  />
                  <YAxis 
                    domain={[0, 28]}
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 11, fill: '#9CA3AF' }}
                    ticks={[0, 7, 14, 21, 28]}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="blinks" 
                    stroke="#000000" 
                    strokeWidth={1}
                    dot={{ fill: '#000000', strokeWidth: 0, r: 1.5 }}
                    activeDot={{ r: 3, fill: '#000000' }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Recent Activity */}
          <div style={styles.activityCard}>
            <div style={styles.activityHeader}>
              <h2 style={styles.activityTitle}>Recent Activity</h2>
              <p style={styles.activitySubtitle}>Last 20 minutes blink activity</p>
            </div>
            <div style={styles.activityList}>
              {recentActivity.map((activity, index) => (
                <div key={index} style={styles.activityItem}>
                  <div style={styles.activityItemLeft}>
                    <div style={styles.activityTime}>{activity.time}</div>
                    <div style={styles.activityBar}>
                      <div 
                        style={{
                          ...styles.activityBarFill,
                          width: `${Math.min((activity.blinks / 30) * 100, 100)}%`
                        }}
                      />
                    </div>
                  </div>
                  <div style={styles.activityCount}>
                    {activity.blinks}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BlinkAnalyticsDashboard;