import "./styles.css";
import { createRoot } from "react-dom/client";
import Toaster from "./components/Toaster.jsx";
import LikeButton from "./components/LikeButton.jsx";
import ModerationPreview from "./components/ModerationPreview.jsx";
import CommentForm from "./components/CommentForm.jsx";
import { toast } from "./toast.js";

// Expose a global so plain scripts (and Jinja) can raise toasts too.
window.socialblog = { toast };

function mount(el, node) {
  createRoot(el).render(node);
}

// --- Toaster (always present) ---------------------------------------------
let toastRoot = document.getElementById("sb-toast-root");
if (!toastRoot) {
  toastRoot = document.createElement("div");
  toastRoot.id = "sb-toast-root";
  document.body.appendChild(toastRoot);
}
mount(toastRoot, <Toaster />);

// --- Bridge server flash messages into toasts -----------------------------
const flashData = document.getElementById("sb-flashes");
if (flashData) {
  try {
    const flashes = JSON.parse(flashData.textContent || "[]");
    const map = { danger: "danger", success: "success", warning: "warning" };
    flashes.forEach(([category, message]) =>
      toast(message, map[category] || "info")
    );
  } catch (_) {
    /* ignore malformed flash payload */
  }
}

// --- Like buttons ----------------------------------------------------------
document.querySelectorAll('[data-island="like-button"]').forEach((el) => {
  mount(
    el,
    <LikeButton
      apiUrl={el.dataset.api}
      loginUrl={el.dataset.login}
      initialCount={Number(el.dataset.count || 0)}
      initialLiked={el.dataset.liked === "true"}
      authed={el.dataset.authed === "true"}
    />
  );
});

// --- Live moderation previews ---------------------------------------------
document.querySelectorAll('[data-island="moderation"]').forEach((el) => {
  const inputs = (el.dataset.inputs || "").split(",").map((s) => s.trim()).filter(Boolean);
  mount(el, <ModerationPreview inputs={inputs} moderateUrl={el.dataset.api} />);
});

// --- Async comment form ----------------------------------------------------
const commentIsland = document.getElementById("comment-form-island");
if (commentIsland) {
  mount(commentIsland, <CommentForm />);
}
