import { useEffect, useRef, useState } from "react";
import { postJSON, debounce } from "../api.js";

// Watches one or more inputs and shows live toxicity feedback as the user
// types, calling the /api/moderate endpoint. Purely advisory — the server
// still enforces moderation on submit.
export default function ModerationPreview({ inputs, moderateUrl }) {
  const [state, setState] = useState({ status: "idle", reason: null });
  const els = useRef([]);

  useEffect(() => {
    els.current = inputs
      .map((id) => document.getElementById(id))
      .filter(Boolean);

    const check = debounce(async () => {
      const text = els.current
        .map((el) => el.value || "")
        .join("\n")
        .trim();
      if (text.length < 3) {
        setState({ status: "idle", reason: null });
        return;
      }
      setState({ status: "checking", reason: null });
      const { ok, data } = await postJSON(moderateUrl, { text });
      if (!ok || !data) {
        setState({ status: "idle", reason: null });
        return;
      }
      if (data.flagged) setState({ status: "flagged", reason: data.reason });
      else setState({ status: "clean", reason: null });
    }, 500);

    els.current.forEach((el) => el.addEventListener("input", check));
    return () => els.current.forEach((el) => el.removeEventListener("input", check));
  }, [inputs, moderateUrl]);

  if (state.status === "idle") return null;

  if (state.status === "checking") {
    return <span className="sb-mod-pill sb-mod-checking">Checking tone…</span>;
  }
  if (state.status === "clean") {
    return <span className="sb-mod-pill sb-mod-clean">✓ Looks respectful</span>;
  }
  return (
    <span className="sb-mod-pill sb-mod-flagged">
      ⚠ May be flagged as {state.reason}
    </span>
  );
}
