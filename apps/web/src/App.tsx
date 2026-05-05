import React from 'react';
import { clamp, randomId } from '@ai-test/utils';
import { ImageUploader } from './components/ImageUploader';

export default function App() {
  const [id] = React.useState(() => randomId(12));
  const [activeTab, setActiveTab] = React.useState<'demo' | 'vision'>('demo');

  return (
    <div style={{ padding: '2rem', fontFamily: 'system-ui, sans-serif' }}>
      <h1>AI Test Web</h1>
      <p>Session ID: <code>{id}</code></p>

      <div style={{ marginBottom: '1rem', borderBottom: '1px solid #eee' }}>
        <button
          onClick={() => setActiveTab('demo')}
          style={{
            padding: '0.5rem 1rem',
            marginRight: '0.5rem',
            background: activeTab === 'demo' ? '#0070f3' : '#f5f5f5',
            color: activeTab === 'demo' ? 'white' : 'black',
            border: 'none',
            borderRadius: '4px 4px 0 0',
            cursor: 'pointer',
          }}
        >
          Demo Utils
        </button>
        <button
          onClick={() => setActiveTab('vision')}
          style={{
            padding: '0.5rem 1rem',
            background: activeTab === 'vision' ? '#0070f3' : '#f5f5f5',
            color: activeTab === 'vision' ? 'white' : 'black',
            border: 'none',
            borderRadius: '4px 4px 0 0',
            cursor: 'pointer',
          }}
        >
          Vision AI
        </button>
      </div>

      {activeTab === 'demo' && (
        <div style={{ padding: '1rem', background: '#f9f9f9', borderRadius: '0 8px 8px 8px' }}>
          <p>Clamped value (150 in range 0-100): {clamp(150, 0, 100)}</p>
        </div>
      )}

      {activeTab === 'vision' && (
        <div style={{ padding: '1rem', background: '#f9f9f9', borderRadius: '0 8px 8px 8px' }}>
          <p style={{ marginBottom: '1rem', color: '#666' }}>
            Connect to Python AI service at <code>http://localhost:8000</code>
          </p>
          <ImageUploader />
        </div>
      )}
    </div>
  );
}
