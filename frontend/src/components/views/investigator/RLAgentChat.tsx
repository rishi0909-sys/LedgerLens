import { useState, useRef, useEffect } from 'react';
import { Send, ThumbsUp, ThumbsDown, BrainCircuit, User } from 'lucide-react';

interface ChatMessage {
  id: string;
  sender: 'agent' | 'user';
  text: string;
  timestamp: string;
}

interface RLAgentChatProps {
  chatHistory: ChatMessage[];
  isTraining: boolean;
  onSendFeedback: (text: string, isPositive: boolean) => void;
}

export function RLAgentChat({ chatHistory, isTraining, onSendFeedback }: RLAgentChatProps) {
  const [inputText, setInputText] = useState('');
  const [feedbackType, setFeedbackType] = useState<boolean | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory, isTraining]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() && feedbackType === null) return;
    
    // Default to positive if they just type and hit send without a button
    onSendFeedback(inputText, feedbackType ?? true);
    setInputText('');
    setFeedbackType(null);
  };

  return (
    <div className="flex flex-col h-full bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
      <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950">
        <div className="flex items-center gap-2">
          <BrainCircuit className="text-blue-400" size={18} />
          <h3 className="text-sm font-bold text-slate-200">RL Copilot Chat</h3>
        </div>
        <div className="text-[10px] uppercase tracking-widest text-slate-500 font-bold bg-slate-900 px-2 py-1 rounded">
          Offline Dataset Builder
        </div>
      </div>

      <div className="flex-1 p-4 overflow-y-auto space-y-4 min-h-[300px]">
        {chatHistory.length === 0 ? (
          <div className="text-center text-slate-500 text-sm mt-12">
            No active conversation. <br />
            Run the simulation to review the agent's prioritization logic.
          </div>
        ) : (
          chatHistory.map((msg) => (
            <div key={msg.id} className={`flex gap-3 ${msg.sender === 'user' ? 'flex-row-reverse' : ''}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                msg.sender === 'agent' ? 'bg-blue-900/50 text-blue-400 border border-blue-500/20' : 'bg-slate-800 text-slate-400'
              }`}>
                {msg.sender === 'agent' ? <BrainCircuit size={16} /> : <User size={16} />}
              </div>
              <div className={`max-w-[80%] rounded-2xl p-3 text-sm ${
                msg.sender === 'user' 
                  ? 'bg-slate-800 text-slate-200 rounded-tr-sm' 
                  : 'bg-blue-900/10 border border-blue-500/20 text-blue-100 rounded-tl-sm'
              }`}>
                {msg.text}
              </div>
            </div>
          ))
        )}
        
        {isTraining && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-blue-900/50 text-blue-400 border border-blue-500/20 flex items-center justify-center shrink-0">
              <BrainCircuit size={16} />
            </div>
            <div className="bg-blue-900/10 border border-blue-500/20 rounded-2xl rounded-tl-sm p-4 flex items-center gap-2 text-blue-400 text-sm">
              <span className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce" />
              <span className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce [animation-delay:0.2s]" />
              <span className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce [animation-delay:0.4s]" />
              <span className="ml-2">Structuring feedback into repository...</span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="p-4 bg-slate-950 border-t border-slate-800">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <button 
            type="button"
            onClick={() => setFeedbackType(true)}
            className={`p-2 rounded-lg transition-colors border ${
              feedbackType === true ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-400' : 'bg-slate-900 border-slate-800 text-slate-500 hover:text-slate-300'
            }`}
          >
            <ThumbsUp size={18} />
          </button>
          <button 
            type="button"
            onClick={() => setFeedbackType(false)}
            className={`p-2 rounded-lg transition-colors border ${
              feedbackType === false ? 'bg-red-500/20 border-red-500/50 text-red-400' : 'bg-slate-900 border-slate-800 text-slate-500 hover:text-slate-300'
            }`}
          >
            <ThumbsDown size={18} />
          </button>
          
          <input 
            type="text" 
            value={inputText}
            onChange={e => setInputText(e.target.value)}
            placeholder="Explain why to add to offline dataset..."
            className="flex-1 min-w-0 bg-slate-900 border border-slate-800 rounded-lg px-4 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
          
          <button 
            type="submit"
            disabled={(!inputText.trim() && feedbackType === null) || isTraining}
            className="bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 disabled:text-slate-600 text-white p-2.5 rounded-lg transition-colors flex items-center justify-center shrink-0"
          >
            <Send size={16} />
          </button>
        </form>
      </div>
    </div>
  );
}
