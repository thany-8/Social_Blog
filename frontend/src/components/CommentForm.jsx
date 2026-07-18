import { useEffect, useState } from "react";
import { postJSON } from "../api.js";
import { toast } from "../toast.js";

// Builds a comment card that matches the server-rendered markup so the shared
// delete-confirmation modal keeps working. Uses textContent for user data to
// stay XSS-safe.
function buildCommentCard(c) {
  const wrap = document.createElement("div");
  wrap.className = "border-top py-3";

  const head = document.createElement("div");
  head.className = "d-flex justify-content-between align-items-center";

  const strong = document.createElement("strong");
  const link = document.createElement("a");
  link.href = c.author_url;
  link.className = "text-decoration-none";
  link.textContent = c.author;
  strong.appendChild(link);

  const date = document.createElement("small");
  date.className = "text-muted";
  date.textContent = c.date;

  head.append(strong, date);

  const body = document.createElement("p");
  body.className = "mb-1";
  body.style.whiteSpace = "pre-wrap";
  body.textContent = c.text;

  wrap.append(head, body);

  if (c.can_delete) {
    const del = document.createElement("button");
    del.type = "button";
    del.className = "btn btn-sm btn-link text-danger p-0";
    del.setAttribute("data-bs-toggle", "modal");
    del.setAttribute("data-bs-target", "#confirmDeleteModal");
    del.setAttribute("data-action", c.delete_url);
    del.setAttribute("data-message", "Delete this comment?");
    del.textContent = "Delete";
    wrap.appendChild(del);
  }
  return wrap;
}

// Enhances the existing comment <form> with async posting. Falls back to a
// normal form submit if this component fails to mount.
export default function CommentForm() {
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const form = document.getElementById("comment-form");
    if (!form) return;
    const textarea = document.getElementById("text");
    const list = document.getElementById("comment-list");
    const apiUrl = form.dataset.api;

    async function onSubmit(e) {
      e.preventDefault();
      const text = (textarea.value || "").trim();
      if (!text) return;
      setBusy(true);
      const { ok, status, data } = await postJSON(apiUrl, { text });
      setBusy(false);

      if (ok && data && data.comment) {
        const empty = document.getElementById("comments-empty");
        if (empty) empty.remove();
        list.appendChild(buildCommentCard(data.comment));
        textarea.value = "";
        textarea.dispatchEvent(new Event("input", { bubbles: true }));
        document.querySelectorAll("[data-comment-count]").forEach((el) => {
          el.textContent = data.count;
        });
        toast("Comment posted!", "success");
      } else if (status === 422 && data) {
        toast(data.error || "Your comment was flagged.", "danger");
      } else {
        toast("Could not post comment. Please try again.", "danger");
      }
    }

    form.addEventListener("submit", onSubmit);
    return () => form.removeEventListener("submit", onSubmit);
  }, []);

  return busy ? (
    <span className="sb-mod-pill sb-mod-checking">Posting…</span>
  ) : null;
}
