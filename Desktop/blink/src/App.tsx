import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import { listen } from '@tauri-apps/api/event';
import "./App.css";
interface BlinkEvent {
  payload: string;
}
function App() {
  
  const [detectionStatus, setDetectionStatus] = useState("");
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    startDetection();
    
    const unlisten = listen('blink-update', (event: BlinkEvent) => {
      setDetectionStatus(event.payload);
    });

    return () => {
      unlisten.then(unlistenFn => unlistenFn());
    };
  }, []);

  async function startDetection() {
    try {
      await invoke("start_detection");
      setIsRunning(true);
    } catch (error) {
      console.error("Failed to start detection:", error);
      setDetectionStatus("Error: Failed to start eye detection");
    }
  }

  return (
    <main className="container">
      <h1>Eye Blink Detection</h1>
      
      <div className="status-container">
        <h2>Detection Status</h2>
        <div className={`status-indicator ${isRunning ? 'running' : 'stopped'}`}>
          {isRunning ? 'Running' : 'Stopped'}
        </div>
        
        <div className="blink-stats">
          {detectionStatus}
        </div>
      </div>

      <div className="controls">
        {!isRunning && (
          <button onClick={startDetection}>
            Start Detection
          </button>
        )}
      </div>
    </main>
  );
}

export default App;