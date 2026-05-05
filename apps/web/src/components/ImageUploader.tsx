import { useState, useRef, useCallback } from 'react';

type TaskType = 'caption' | 'detect' | 'ocr';

interface Detection {
  class_name: string;
  confidence: number;
  bbox: [number, number, number, number];
}

interface Result {
  task?: string;
  caption?: string;
  detections?: Detection[];
  full_text?: string;
  results?: { text: string; confidence: number }[];
  processing_time_ms?: number;
}

const API_BASE = 'http://localhost:8000';

export function ImageUploader() {
  const [image, setImage] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<Result | null>(null);
  const [task, setTask] = useState<TaskType>('caption');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = useCallback((selectedFile: File) => {
    if (!selectedFile.type.startsWith('image/')) {
      setError('Please select an image file');
      return;
    }
    setFile(selectedFile);
    setError(null);
    const reader = new FileReader();
    reader.onload = (e) => setImage(e.target?.result as string);
    reader.readAsDataURL(selectedFile);
    setResult(null);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      handleFileSelect(droppedFile);
    }
  }, [handleFileSelect]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setDragOver(false);
  }, []);

  const handleSubmit = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);

    const endpoints: Record<TaskType, string> = {
      caption: `${API_BASE}/vision/caption`,
      detect: `${API_BASE}/vision/detect`,
      ocr: `${API_BASE}/vision/ocr`,
    };

    try {
      const res = await fetch(endpoints[task], {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        throw new Error(`API error: ${res.status}`);
      }

      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process image');
    } finally {
      setLoading(false);
    }
  };

  const renderResult = () => {
    if (!result) return null;

    if (task === 'caption') {
      return (
        <div className="result-box">
          <h3>Caption</h3>
          <p className="caption-text">"{result.caption}"</p>
          <p className="time">Processed in {result.processing_time_ms?.toFixed(0)}ms</p>
        </div>
      );
    }

    if (task === 'detect' && result.detections) {
      return (
        <div className="result-box">
          <h3>Detections ({result.detections.length} objects)</h3>
          <ul className="detection-list">
            {result.detections.map((det, i) => (
              <li key={i}>
                <span className="class-name">{det.class_name}</span>
                <span className="confidence">{(det.confidence * 100).toFixed(1)}%</span>
              </li>
            ))}
          </ul>
          <p className="time">Processed in {result.processing_time_ms?.toFixed(0)}ms</p>
        </div>
      );
    }

    if (task === 'ocr') {
      return (
        <div className="result-box">
          <h3>Extracted Text</h3>
          <pre className="ocr-text">{result.full_text || ''}</pre>
          <p className="time">Processed in {result.processing_time_ms?.toFixed(0)}ms</p>
        </div>
      );
    }

    return null;
  };

  return (
    <div className="uploader">
      <div className="controls">
        <select value={task} onChange={(e) => setTask(e.target.value as TaskType)}>
          <option value="caption">Image Captioning</option>
          <option value="detect">Object Detection</option>
          <option value="ocr">OCR Text Extraction</option>
        </select>
      </div>

      <div
        className={`drop-zone ${dragOver ? 'drag-over' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
          hidden
        />
        {image ? (
          <img src={image} alt="Preview" className="preview" />
        ) : (
          <div className="placeholder">
            <span>Drop an image here or click to select</span>
          </div>
        )}
      </div>

      {error && <div className="error">{error}</div>}

      <button onClick={handleSubmit} disabled={!file || loading}>
        {loading ? 'Processing...' : 'Analyze'}
      </button>

      {renderResult()}

      <style>{`
        .uploader {
          max-width: 600px;
          margin: 0 auto;
          padding: 1rem;
        }
        .controls {
          margin-bottom: 1rem;
        }
        .controls select {
          padding: 0.5rem 1rem;
          font-size: 1rem;
          border-radius: 6px;
          border: 1px solid #ccc;
          background: white;
        }
        .drop-zone {
          border: 2px dashed #ccc;
          border-radius: 12px;
          padding: 2rem;
          text-align: center;
          cursor: pointer;
          transition: all 0.2s;
          min-height: 200px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: #fafafa;
        }
        .drop-zone:hover, .drop-zone.drag-over {
          border-color: #0070f3;
          background: #f0f7ff;
        }
        .placeholder {
          color: #666;
        }
        .preview {
          max-width: 100%;
          max-height: 400px;
          border-radius: 8px;
        }
        button {
          margin-top: 1rem;
          width: 100%;
          padding: 0.75rem 1.5rem;
          font-size: 1rem;
          background: #0070f3;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
        }
        button:hover:not(:disabled) {
          background: #005bb5;
        }
        button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
        .error {
          margin-top: 1rem;
          padding: 0.75rem;
          background: #fee;
          color: #c00;
          border-radius: 6px;
        }
        .result-box {
          margin-top: 1.5rem;
          padding: 1rem;
          background: #f5f5f5;
          border-radius: 8px;
        }
        .result-box h3 {
          margin: 0 0 0.75rem 0;
          font-size: 1rem;
        }
        .caption-text {
          font-size: 1.1rem;
          font-style: italic;
          color: #333;
        }
        .ocr-text {
          background: white;
          padding: 1rem;
          border-radius: 6px;
          white-space: pre-wrap;
          max-height: 300px;
          overflow-y: auto;
        }
        .detection-list {
          list-style: none;
          padding: 0;
          margin: 0;
        }
        .detection-list li {
          display: flex;
          justify-content: space-between;
          padding: 0.5rem;
          background: white;
          margin-bottom: 0.25rem;
          border-radius: 4px;
        }
        .class-name {
          text-transform: capitalize;
        }
        .confidence {
          color: #666;
        }
        .time {
          margin-top: 0.75rem;
          font-size: 0.875rem;
          color: #666;
        }
      `}</style>
    </div>
  );
}
