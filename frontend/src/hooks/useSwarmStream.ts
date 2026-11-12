import { useState, useCallback, useRef } from 'react';
import { LogEntry } from '../types/agent';

interface UseSwarmStreamOptions {
  onEvent?: (event: any) => void;
  onError?: (error: any) => void;
  onComplete?: () => void;
}

export function useSwarmStream(options: UseSwarmStreamOptions = {}) {
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamLogs, setStreamLogs] = useState<LogEntry[]>([]);
  const [streamError, setStreamError] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  const connectStream = useCallback((url: string) => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    setIsStreaming(true);
    setStreamError(null);

    const es = new EventSource(url);
    eventSourceRef.current = es;

    es.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        options.onEvent?.(data);

        if (data.type === 'workflow_completed') {
          setIsStreaming(false);
          options.onComplete?.();
          es.close();
        }
      } catch (err) {
        console.error('Failed to parse SSE event data:', err);
      }
    };

    es.onerror = (err) => {
      console.error('SSE Stream error:', err);
      setStreamError('Connection interrupted or completed.');
      setIsStreaming(false);
      options.onError?.(err);
      es.close();
    };
  }, [options]);

  const closeStream = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setIsStreaming(false);
  }, []);

  return {
    isStreaming,
    streamLogs,
    streamError,
    connectStream,
    closeStream,
  };
}
