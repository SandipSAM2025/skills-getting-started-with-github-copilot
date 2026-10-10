document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  function escapeHtml(str) {
    if (typeof str !== "string") return str;
    return str
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      activitiesList.innerHTML = "";
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        const participants = details.participants || [];
        const participantsHtml = participants.length
          ? `<div class="participants">
               <strong>Participants:</strong>
               <ul class="participants-list">
                 ${participants
                   .map(
                     (p) => `
                       <li class="participant-item">
                         <span class="participant-email">${escapeHtml(p)}</span>
                         <button
                           class="participant-delete"
                           data-activity="${escapeHtml(name)}"
                           data-email="${escapeHtml(p)}"
                           type="button"
                           title="Remove participant"
                         >✖</button>
                       </li>
                     `
                   )
                   .join("")}
               </ul>
             </div>`
          : `<div class="participants"><strong>Participants:</strong> <span class="none">None yet</span></div>`;

        activityCard.innerHTML = `
          <h4>${escapeHtml(name)}</h4>
          <p>${escapeHtml(details.description)}</p>
          <p><strong>Schedule:</strong> ${escapeHtml(details.schedule)}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          ${participantsHtml}
        `;

        activitiesList.appendChild(activityCard);

        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });

      document.querySelectorAll(".participant-delete").forEach((btn) => {
        btn.addEventListener("click", async () => {
          const activityName = btn.getAttribute("data-activity");
          const email = btn.getAttribute("data-email");

          const confirmed = confirm(`Remove ${email} from ${activityName}?`);
          if (!confirmed) return;

          try {
            const response = await fetch(
              `/activities/${encodeURIComponent(activityName)}/participants?email=${encodeURIComponent(email)}`,
              {
                method: "DELETE",
              }
            );

            const result = await response.json();

            if (response.ok) {
              await fetchActivities();
              messageDiv.textContent = result.message;
              messageDiv.className = "message success";
            } else {
              messageDiv.textContent = result.detail || "Failed to remove participant";
              messageDiv.className = "message error";
            }

            messageDiv.classList.remove("hidden");
            setTimeout(() => {
              messageDiv.classList.add("hidden");
            }, 5000);
          } catch (error) {
            console.error("Error removing participant:", error);
            messageDiv.textContent = "Failed to remove participant";
            messageDiv.className = "message error";
            messageDiv.classList.remove("hidden");
          }
        });
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const submitBtn = signupForm.querySelector('button[type="submit"]');
      submitBtn.disabled = true;

      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "message success";
        signupForm.reset();
        await fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "message error";
      }

      messageDiv.classList.remove("hidden");
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);

      submitBtn.disabled = false;
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "message error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);

      const submitBtn = signupForm.querySelector('button[type="submit"]');
      if (submitBtn) submitBtn.disabled = false;
    }
  });

  fetchActivities();
});