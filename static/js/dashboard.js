document.addEventListener("DOMContentLoaded", function() {
  // Card hover shadow
  document.querySelectorAll(".card").forEach(card => {
    card.addEventListener("mouseenter", () => card.classList.add("shadow-lg"));
    card.addEventListener("mouseleave", () => card.classList.remove("shadow-lg"));
  });

  // Fade-in animation for cards
  document.querySelectorAll(".card").forEach((card, i) => {
    card.style.opacity = 0;
    setTimeout(() => {
      card.style.transition = "opacity 0.6s ease-in";
      card.style.opacity = 1;
    }, i * 150); // staggered animation
  });

  // Notification simulation
  const notifyBtn = document.getElementById("notifyBtn");
  if (notifyBtn) {
    notifyBtn.addEventListener("click", () => {
      showNotification("🔔 You have new job applications!");
    });
  }

  // Auto notification every 20 seconds
  function autoNotify() {
    showNotification("💡 Tip: Update your profile to attract more employers!");
    setTimeout(autoNotify, 20000);
  }
  setTimeout(autoNotify, 20000);

  // Helper to show notification
  function showNotification(message) {
    const msg = document.createElement("div");
    msg.className = "alert alert-info mt-2";
    msg.innerText = message;
    document.body.prepend(msg);
    setTimeout(() => msg.remove(), 5000);
  }

  // Theme toggle
  const themeToggle = document.createElement("button");
  themeToggle.innerText = "🌙 Toggle Theme";
  themeToggle.className = "btn btn-sm btn-secondary position-fixed bottom-0 end-0 m-3";
  document.body.appendChild(themeToggle);

  themeToggle.addEventListener("click", () => {
    document.body.classList.toggle("dark-mode");
  });
});
