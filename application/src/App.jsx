import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer } from 'recharts';
import { Calendar, Eye, HelpCircle, TrendingUp } from 'lucide-react';

const BlinkAnalyticsDashboard = () => {
  const [blinkRateData, setBlinkRateData] = useState([]);
  const [recentActivity, setRecentActivity] = useState([]);
  const [currentStats, setCurrentStats] = useState({
    averageBlinks: 17.0,
    last20Minutes: 21.5,
    totalToday: 24580,
    percentageAbove: 26.2
  });

  useEffect(() => {
    const fetchData = async () => {
      const [rateRes, activityRes, statsRes] = await Promise.all([
        fetch('http://127.0.0.1:5000/api/blink-rate'),
        fetch('http://127.0.0.1:5000/api/recent-activity'),
        fetch('http://127.0.0.1:5000/api/stats')
      ]);
  
      setBlinkRateData(await rateRes.json());
      setRecentActivity(await activityRes.json());
      setCurrentStats(await statsRes.json());
    };
  
    fetchData();
    const interval = setInterval(fetchData, 30000);
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