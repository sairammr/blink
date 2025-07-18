import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer } from 'recharts';
import { Calendar, Eye, HelpCircle, TrendingUp, Settings, Power } from 'lucide-react';
import CalendarPicker from 'react-calendar';
import 'react-calendar/dist/Calendar.css';

const SettingsModal = ({ isOpen, onClose, onStart, onStop, onSensitivityChange, isTracking, sensitivity }) => {
  const [tempSensitivity, setTempSensitivity] = useState(sensitivity);

  useEffect(() => {
    setTempSensitivity(sensitivity);
  }, [sensitivity]);

  if (!isOpen) return null;

  const styles = {
    overlay: {
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
    },
    modal: {
      backgroundColor: 'white',
      borderRadius: '8px',
      padding: '24px',
      width: '400px',
      boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    },
    header: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: '24px',
    },
    title: {
      fontSize: '20px',
      fontWeight: '600',
      margin: 0,
    },
    closeButton: {
      background: 'none',
      border: 'none',
      cursor: 'pointer',
      padding: '4px',
    },
    content: {
      display: 'flex',
      flexDirection: 'column',
      gap: '20px',
    },
    buttonGroup: {
      display: 'flex',
      gap: '12px',
    },
    button: {
      flex: 1,
      padding: '12px',
      borderRadius: '6px',
      border: 'none',
      cursor: 'pointer',
      fontWeight: '500',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '8px',
    },
    startButton: {
      backgroundColor: '#10B981',
      color: 'white',
    },
    stopButton: {
      backgroundColor: '#EF4444',
      color: 'white',
    },
    disabledButton: {
      opacity: 0.5,
      cursor: 'not-allowed',
    },
    sliderContainer: {
      display: 'flex',
      flexDirection: 'column',
      gap: '8px',
    },
    sliderLabel: {
      fontSize: '14px',
      color: '#6B7280',
    },
    slider: {
      width: '100%',
    },
    confirmButton: {
      backgroundColor: '#3B82F6',
      color: 'white',
      padding: '8px 16px',
      borderRadius: '6px',
      border: 'none',
      cursor: 'pointer',
      fontWeight: '500',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '8px',
      marginTop: '8px',
    },
    confirmButtonDisabled: {
      opacity: 0.5,
      cursor: 'not-allowed',
    },
  };

  const handleConfirmSensitivity = () => {
    onSensitivityChange(tempSensitivity);
  };

  return (
    <div style={styles.overlay} onClick={onClose}>
      <div style={styles.modal} onClick={e => e.stopPropagation()}>
        <div style={styles.header}>
          <h2 style={styles.title}>Settings</h2>
          <button style={styles.closeButton} onClick={onClose}>
            <Settings size={20} />
          </button>
        </div>
        <div style={styles.content}>
          <div style={styles.buttonGroup}>
            <button
              style={{
                ...styles.button,
                ...styles.startButton,
                ...(isTracking ? styles.disabledButton : {}),
              }}
              onClick={onStart}
              disabled={isTracking}
            >
              <Power size={16} />
              Start Tracking
            </button>
            <button
              style={{
                ...styles.button,
                ...styles.stopButton,
                ...(!isTracking ? styles.disabledButton : {}),
              }}
              onClick={onStop}
              disabled={!isTracking}
            >
              <Power size={16} />
              Stop Tracking
            </button>
          </div>
          <div style={styles.sliderContainer}>
            <label style={styles.sliderLabel}>Sensitivity: {tempSensitivity}</label>
            <input
              type="range"
              min="20"
              max="50"
              value={tempSensitivity}
              onChange={(e) => setTempSensitivity(parseInt(e.target.value))}
              style={styles.slider}
            />
            <button
              style={{
                ...styles.confirmButton,
                ...(tempSensitivity === sensitivity ? styles.confirmButtonDisabled : {}),
              }}
              onClick={handleConfirmSensitivity}
              disabled={tempSensitivity === sensitivity}
            >
              Confirm Sensitivity
            </button>
          </div>
        </div>
      </div>
    </div>
  );
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
  const [tenMinAvg, setTenMinAvg] = useState({ average: 0, count: 0 });
  const [todayEntries, setTodayEntries] = useState({ average: 0, count: 0 });
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isTracking, setIsTracking] = useState(false);
  const [sensitivity, setSensitivity] = useState(34);
  const [trackingStatus, setTrackingStatus] = useState('Not Started');
  const [lastMinuteAvg, setLastMinuteAvg] = useState({ average: 0, count: 0 });
  const [lastEntry, setLastEntry] = useState({ timestamp: null, blink_count: null });
  // Calendar and metrics state
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [dateMetrics, setDateMetrics] = useState({ average_blinks: 0, max_blinks: 0, min_blinks: 0, count: 0, date: '' });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [rateRes, activityRes, statsRes, statusRes, tenMinRes, todayEntriesRes, lastMinRes, lastEntryRes] = await Promise.all([
          fetch('http://127.0.0.1:5000/api/blink-rate'),
          fetch('http://127.0.0.1:5000/api/recent-activity'),
          fetch('http://127.0.0.1:5000/api/stats'),
          fetch('http://127.0.0.1:5000/status'),
          fetch('http://127.0.0.1:5000/api/10min-average'),
          fetch('http://127.0.0.1:5000/api/today-entries'),
          fetch('http://127.0.0.1:5000/api/last-minute-average'),
          fetch('http://127.0.0.1:5000/api/last-entry')
        ]);
        setBlinkRateData(await rateRes.json());
        setRecentActivity(await activityRes.json());
        setCurrentStats(await statsRes.json());
        const statusData = await statusRes.json();
        setTrackingStatus(statusData.status);
        setIsTracking(statusData.running);
        setTenMinAvg(await tenMinRes.json());
        setTodayEntries(await todayEntriesRes.json());
        setLastMinuteAvg(await lastMinRes.json());
        setLastEntry(await lastEntryRes.json());
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  // Fetch metrics when selectedDate changes
  useEffect(() => {
    const fetchMetrics = async () => {
      const dateStr = selectedDate.toISOString().slice(0, 10);
      try {
        const res = await fetch('http://127.0.0.1:5000/api/metrics-by-date', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ date: dateStr })
        });
        if (res.ok) {
          setDateMetrics(await res.json());
        } else {
          setDateMetrics({ average_blinks: 0, max_blinks: 0, min_blinks: 0, count: 0, date: dateStr });
        }
      } catch {
        setDateMetrics({ average_blinks: 0, max_blinks: 0, min_blinks: 0, count: 0, date: dateStr });
      }
    };
    if (selectedDate) fetchMetrics();
  }, [selectedDate]);

  const handleStartTracking = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/start', { method: 'POST' });
      if (response.ok) {
        setIsTracking(true);
      }
    } catch (error) {
      console.error('Error starting tracking:', error);
    }
  };

  const handleStopTracking = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/stop', { method: 'POST' });
      if (response.ok) {
        setIsTracking(false);
      }
    } catch (error) {
      console.error('Error stopping tracking:', error);
    }
  };

  const handleSensitivityChange = async (value) => {
    try {
      const response = await fetch('http://127.0.0.1:5000/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ threshold: parseInt(value) }),
      });
      if (response.ok) {
        setSensitivity(parseInt(value));
      }
    } catch (error) {
      console.error('Error updating sensitivity:', error);
    }
  };

  const styles = {
    container: {
      minHeight: '100vh',
      backgroundColor: 'white',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      overflow: 'hidden',
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
      display: 'flex',
      alignItems: 'center',
      gap: '16px'
    },
    statusIndicator: {
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      fontSize: '14px',
      color: '#6b7280'
    },
    statusDot: {
      width: '8px',
      height: '8px',
      borderRadius: '50%',
      transition: 'all 0.3s ease'
    },
    statusDotActive: {
      backgroundColor: '#10B981',
      boxShadow: '0 0 8px #10B981'
    },
    statusDotInactive: {
      backgroundColor: '#EF4444',
      boxShadow: '0 0 8px #EF4444'
    },
    settingsButton: {
      background: 'none',
      border: 'none',
      cursor: 'pointer',
      padding: '8px',
      borderRadius: '4px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      color: '#6b7280',
      transition: 'all 0.2s ease'
    },
    settingsButtonHover: {
      backgroundColor: '#f3f4f6'
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
            <div style={styles.statusIndicator}>
              <div 
                style={{
                  ...styles.statusDot,
                  ...(isTracking ? styles.statusDotActive : styles.statusDotInactive)
                }} 
              />
              <span>{trackingStatus}</span>
            </div>
            <button 
              style={styles.settingsButton}
              onClick={() => setIsSettingsOpen(true)}
            >
              <Settings size={20} />
            </button>
          </div>
        </div>
      </div>

      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        onStart={handleStartTracking}
        onStop={handleStopTracking}
        onSensitivityChange={handleSensitivityChange}
        isTracking={isTracking}
        sensitivity={sensitivity}
      />

      {/* Main Content */}
      <div style={styles.main}>
        {/* Page Header */}
        <div style={styles.pageHeader}>
          <h1 style={styles.pageTitle}>Blink Data Analysis</h1>
          <div style={styles.dateInfo}>
            <Calendar size={16} />
            <span>{new Date().toLocaleDateString()}</span>
          </div>
        </div>
        {/* Stats Cards */}
        <div style={{ ...styles.statsGrid, gridTemplateColumns: 'repeat(5, 1fr)' }}>
          {/* Last Entry Tile */}
          <div style={styles.statsCard}>
            <div style={styles.statsHeader}>
              <h3 style={styles.statsTitle}>Last Entry</h3>
              <Eye size={16} color="#d1d5db" />
            </div>
            <div style={styles.statsValue}>
              {lastEntry.blink_count !== null ? `${lastEntry.blink_count} blinks` : 'N/A'}
            </div>
            <p style={styles.statsSubtext}>
              {lastEntry.timestamp ? `at ${lastEntry.timestamp}` : 'No data'}
            </p>
          </div>
          {/* 10-Minute Average Tile */}
          <div style={styles.statsCard}>
            <div style={styles.statsHeader}>
              <h3 style={styles.statsTitle}>Last 10-Minute Avg</h3>
              <HelpCircle size={16} color="#d1d5db" />
            </div>
            <div style={styles.statsValue}>
              {tenMinAvg.average.toFixed(1)} blinks/min
            </div>
            <p style={styles.statsSubtext}>{tenMinAvg.count} entries</p>
          </div>
          {/* Last 20 Minutes Tile */}
          <div style={styles.statsCard}>
            <div style={styles.statsHeader}>
              <h3 style={styles.statsTitle}>Last 20 Minutes Avg</h3>
              <HelpCircle size={16} color="#d1d5db" />
            </div>
            <div style={styles.statsValue}>
              {currentStats.last20Minutes.toFixed(1)} blinks/min
            </div>
            <p style={styles.statsSubtext}>
              +{Math.abs(currentStats.percentageAbove).toFixed(1)}% above average
            </p>
          </div>
          {/* Today's Average Tile */}
          <div style={styles.statsCard}>
            <div style={styles.statsHeader}>
              <h3 style={styles.statsTitle}>Today's Avg</h3>
              <HelpCircle size={16} color="#d1d5db" />
            </div>
            <div style={styles.statsValue}>
              {todayEntries.average.toFixed(1)} blinks/min
            </div>
            <p style={styles.statsSubtext}>{todayEntries.count} entries</p>
          </div>
          {/* Total Blinks Today Tile */}
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
                    {/* Calendar and Metrics at the bottom */}
        <div style={{ display: 'flex', gap: '32px', alignItems: 'flex-start', marginTop: '48px', justifyContent: 'start' }}>
          <div>
            <CalendarPicker
              onChange={setSelectedDate}
              value={selectedDate}
              maxDate={new Date()}
            />
          </div>
          <div style={{ minWidth: 220, background: 'white', border: '1px solid #e5e7eb', borderRadius: 8, padding: 24 }}>
            <h3 style={{ fontSize: 16, fontWeight: 600, margin: 0, marginBottom: 8 }}>Metrics for {dateMetrics.date}</h3>
            <div style={{ fontSize: 14, color: '#374151', marginBottom: 6 }}>Average: <b>{dateMetrics.average_blinks}</b> blinks/min</div>
            <div style={{ fontSize: 14, color: '#374151', marginBottom: 6 }}>Highest: <b>{dateMetrics.max_blinks}</b> blinks/min</div>
            <div style={{ fontSize: 14, color: '#374151', marginBottom: 6 }}>Lowest: <b>{dateMetrics.min_blinks}</b> blinks/min</div>
            <div style={{ fontSize: 12, color: '#9ca3af' }}>{dateMetrics.count} entries</div>
          </div>
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