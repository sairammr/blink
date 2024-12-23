import React, { useRef, useState, useEffect } from 'react';
import { X, Maximize2 } from 'lucide-react';

export function CameraPreview() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [stream, setStream] = useState<MediaStream | null>(null);

  useEffect(() => {
    async function setupCamera() {
      try {
        const mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
        setStream(mediaStream);
        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
        }
      } catch (err) {
        console.error("Error accessing camera:", err);
      }
    }
    setupCamera();

    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  return (
    <div className={`relative ${isFullscreen ? 'fixed inset-0 z-50 bg-black/90 backdrop-blur-sm' : 'h-[500px]'}`}>
      <div className={`
        ${isFullscreen 
          ? 'absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[90vw] h-[90vh]' 
          : 'w-full h-full'
        }
      `}>
        <video
          ref={videoRef}
          autoPlay
          playsInline
          className={`
            rounded-2xl shadow-lg
            ${isFullscreen 
              ? 'w-full h-full object-contain' 
              : 'w-full h-full object-cover hover:scale-[1.02] transition-transform duration-300'
            }
          `}
        />
        <div className={`
          absolute top-4 right-4 space-x-2
          ${!isFullscreen && 'opacity-0 group-hover:opacity-100 transition-opacity duration-300'}
        `}>
          {!isFullscreen && (
            <button
              onClick={() => setIsFullscreen(true)}
              className="p-3 bg-white/20 hover:bg-white/30 backdrop-blur-md rounded-xl text-white transition-colors shadow-lg"
            >
              <Maximize2 className="w-5 h-5" />
            </button>
          )}
          {isFullscreen && (
            <button
              onClick={() => setIsFullscreen(false)}
              className="p-3 bg-white/20 hover:bg-white/30 backdrop-blur-md rounded-xl text-white transition-colors shadow-lg"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}