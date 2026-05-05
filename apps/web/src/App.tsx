import React from 'react';
import { clamp, randomId } from '@ai-test/utils';

export default function App() {
  const [id] = React.useState(() => randomId(12));

  return (
    <div style={{ padding: '2rem', fontFamily: 'system-ui, sans-serif' }}>
      <h1>AI Test Web</h1>
      <p>Session ID: <code>{id}</code></p>
      <p>Clamped value (150 in range 0-100): {clamp(150, 0, 100)}</p>
    </div>
  );
}
