import { useState } from "react";
import { postJSON } from "../api.js";
import { toast } from "../toast.js";

// Async like/unlike button. Replaces the server-rendered like form so the
// count updates without a page reload.
export default function LikeButton({ apiUrl, loginUrl, initialCount, initialLiked, authed }) {
  const [count, setCount] = useState(initialCount);
  const [liked, setLiked] = useState(initialLiked);
  const [busy, setBusy] = useState(false);
  const [pop, setPop] = useState(false);

  async function onClick() {
    if (!authed) {
      toast("Log in to like posts.", "info");
      if (loginUrl) setTimeout(() => (window.location.href = loginUrl), 600);
      return;
    }
    if (busy) return;
    setBusy(true);
    const { ok, data } = await postJSON(apiUrl);
    setBusy(false);
    if (ok && data) {
      setCount(data.count);
      setLiked(data.liked);
      setPop(true);
      setTimeout(() => setPop(false), 300);
    } else {
      toast("Could not update like. Please try again.", "danger");
    }
  }

  return (
    <button
      type="button"
      onClick={onClick}
      disabled={busy}
      aria-pressed={liked}
      className={`btn btn-sm rounded-pill ${liked ? "btn-danger" : "btn-outline-danger"} ${
        pop ? "sb-like-pop" : ""
      }`}
    >
      ❤ {count}
    </button>
  );
}
