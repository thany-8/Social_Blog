import { useEffect, useState } from "react";
import { subscribe } from "../toast.js";

const ICONS = { info: "ℹ️", success: "✅", danger: "⛔", warning: "⚠️" };

// Renders transient toast notifications raised anywhere via toast().
export default function Toaster() {
  const [toasts, setToasts] = useState([]);

  useEffect(() => {
    return subscribe((t) => {
      setToasts((cur) => [...cur, t]);
      setTimeout(() => {
        setToasts((cur) => cur.filter((x) => x.id !== t.id));
      }, 4500);
    });
  }, []);

  const dismiss = (id) => setToasts((cur) => cur.filter((x) => x.id !== id));

  return (
    <div className="sb-toast-wrap" role="status" aria-live="polite">
      {toasts.map((t) => (
        <div key={t.id} className={`sb-toast sb-toast-${t.type}`}>
          <span>{ICONS[t.type] || ICONS.info}</span>
          <span>{t.message}</span>
          <button aria-label="Dismiss" onClick={() => dismiss(t.id)}>
            ×
          </button>
        </div>
      ))}
    </div>
  );
}
