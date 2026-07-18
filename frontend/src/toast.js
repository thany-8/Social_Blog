// A tiny pub/sub bus so any island (or plain JS) can raise a toast.
// Toasts raised before the Toaster has subscribed are buffered and flushed on
// subscribe (React 18 runs effects after the initial render, so main.jsx may
// raise server-flash toasts before the Toaster is listening).

const listeners = new Set();
const buffer = [];

export function toast(message, type = "info") {
  const payload = { id: `${Date.now()}-${Math.random()}`, message, type };
  if (listeners.size === 0) {
    buffer.push(payload);
    return;
  }
  listeners.forEach((fn) => fn(payload));
}

export function subscribe(fn) {
  listeners.add(fn);
  if (buffer.length) {
    buffer.splice(0).forEach((payload) => fn(payload));
  }
  return () => listeners.delete(fn);
}
