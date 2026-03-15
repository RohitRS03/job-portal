<script>
document.addEventListener("DOMContentLoaded", function() {
  // Smooth scroll to section when card clicked
  document.querySelectorAll(".square-card").forEach(card => {
    card.addEventListener("click", function() {
      const target = card.getAttribute("data-bs-target");
      if (target) {
        const section = document.querySelector(target);
        if (section) {
          section.classList.add("show"); // expand collapse
          section.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      }
    });
  })
});
</script>
