function ChatMessage({ message }) {
  return (
    <div className="message">
      <div className="message-content">
        {message.content}
        
        {message.confidence && (
          <div className={`confidence-badge ${getConfidenceClass(message.confidence)}`}>
            {message.confidence_label} ({Math.round(message.confidence * 100)}%)
          </div>
        )}
        
        {message.sources && message.sources.length > 0 && (
          <div className="sources">
            <details>
              <summary>Sources</summary>
              <ul>
                {message.sources.map((source, idx) => (
                  <li key={idx}>{source}</li>
                ))}
              </ul>
            </details>
          </div>
        )}
      </div>
    </div>
  );
}

function getConfidenceClass(score) {
  if (score >= 0.8) return 'high-confidence';
  if (score >= 0.5) return 'medium-confidence';
  return 'low-confidence';
} 