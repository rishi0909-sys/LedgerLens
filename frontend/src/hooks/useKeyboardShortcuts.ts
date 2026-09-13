import { useEffect } from 'react';

export function useKeyboardShortcuts(actions: {
  onNext?: () => void;
  onPrev?: () => void;
  onEnter?: () => void;
  onRL?: () => void;
  onEscape?: () => void;
  onCmdK?: () => void;
}) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't trigger shortcuts if user is typing in an input
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        actions.onCmdK?.();
      } else if (e.key === 'j') {
        actions.onNext?.();
      } else if (e.key === 'k') {
        actions.onPrev?.();
      } else if (e.key === 'Enter') {
        actions.onEnter?.();
      } else if (e.key === 'r' || e.key === 'R') {
        actions.onRL?.();
      } else if (e.key === 'Escape') {
        actions.onEscape?.();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [actions]);
}
