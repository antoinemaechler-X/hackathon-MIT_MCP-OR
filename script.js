let commentCount = 0;
let map = null;
let startMarker = null;
let endMarker = null;

function prompt_model(comment) {
  // Stub for future backend call
  return Promise.resolve({ status: "success" });
}

async function solve_model(start, end, preferences) {
  return fetch("http://127.0.0.1:8000/api/solve", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      start,
      end,
      preferences,
    }),
  }).then((res) => res.json());
}

function initMap() {
  // Initialize map centered on the US
  map = L.map("map").setView([39.8283, -98.5795], 4);

  // Add OpenStreetMap tiles
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "© OpenStreetMap contributors",
  }).addTo(map);
}

function updateMap(startCoords, endCoords) {
  // Clear existing markers
  if (startMarker) map.removeLayer(startMarker);
  if (endMarker) map.removeLayer(endMarker);

  // Add new markers
  startMarker = L.marker([startCoords[0], startCoords[1]], {
    icon: L.divIcon({
      className: "start-marker",
      html: '<div style="background-color: blue; width: 20px; height: 20px; border-radius: 50%;"></div>',
    }),
  }).addTo(map);

  endMarker = L.marker([endCoords[0], endCoords[1]], {
    icon: L.divIcon({
      className: "end-marker",
      html: '<div style="background-color: red; width: 20px; height: 20px; border-radius: 50%;"></div>',
    }),
  }).addTo(map);

  // Fit map to show both markers
  const bounds = L.latLngBounds([
    startMarker.getLatLng(),
    endMarker.getLatLng(),
  ]);
  map.fitBounds(bounds, { padding: [50, 50] });
}

document.addEventListener("DOMContentLoaded", () => {
  const bg = document.querySelector(".background");

  // Initialize sliders
  const timeSlider = document.getElementById("time-slider");
  const costSlider = document.getElementById("cost-slider");
  const emissionsSlider = document.getElementById("emissions-slider");
  const timeThumb = document.getElementById("time-thumb");
  const costThumb = document.getElementById("cost-thumb");
  const emissionsThumb = document.getElementById("emissions-thumb");

  // Update slider thumbs on slider change
  function updateSliderPosition(slider, thumb) {
    const percent = 100 - slider.value;
    const thumbPosition = (percent / 100) * slider.parentElement.clientHeight;
    thumb.style.top = `${thumbPosition}px`;

    // Adjust glow intensity based on value
    const glowIntensity = 0.3 + (slider.value / 100) * 0.7;
    thumb.style.boxShadow = `0 0 ${
      15 * glowIntensity
    }px rgba(255, 255, 255, ${glowIntensity})`;
  }

  // Initialize slider positions
  updateSliderPosition(timeSlider, timeThumb);
  updateSliderPosition(costSlider, costThumb);
  updateSliderPosition(emissionsSlider, emissionsThumb);

  // Event listeners for sliders
  timeSlider.addEventListener("input", () =>
    updateSliderPosition(timeSlider, timeThumb)
  );
  costSlider.addEventListener("input", () =>
    updateSliderPosition(costSlider, costThumb)
  );
  emissionsSlider.addEventListener("input", () =>
    updateSliderPosition(emissionsSlider, emissionsThumb)
  );

  // Initialize map when page loads
  initMap();

  // ---- wire up your button ----
  const btn = document.getElementById("solve-model");
  btn.addEventListener("click", async () => {
    const start = document.getElementById("start").value.trim();
    const end = document.getElementById("end").value.trim();
    if (!start || !end) {
      document.getElementById("output").textContent =
        "Please enter both addresses.";
      return;
    }

    // Get preferences from sliders
    const preferences = {
      timeImportance: parseInt(timeSlider.value),
      costImportance: parseInt(costSlider.value),
      emissionsImportance: parseInt(emissionsSlider.value),
    };

    try {
      const result = await solve_model(start, end, preferences);
      document.getElementById("output").textContent = JSON.stringify(
        result,
        null,
        2
      );

      // Update map with coordinates if available
      if (result.coords_start && result.coords_end) {
        updateMap(result.coords_start, result.coords_end);
      }
    } catch (err) {
      document.getElementById("output").textContent =
        "Error contacting backend.";
    }
  });

  // Send comment functionality
  const sendCommentBtn = document.getElementById("send");
  const commentInput = document.getElementById("comment");
  const commentsContainer = document.getElementById("comments");

  sendCommentBtn.addEventListener("click", async () => {
    const commentText = commentInput.value.trim();
    if (commentText) {
      const commentPill = document.createElement("div");
      commentPill.className = "comment-pill";
      commentPill.textContent = commentText;
      commentsContainer.appendChild(commentPill);
      commentInput.value = "";

      // Optional: Send to backend
      await prompt_model(commentText);
      commentCount++;
    }
  });

  const iconNames = [
    "box-fill.svg",
    "train-freight-front.svg",
    "car-front.svg",
    "signpost-split.svg",
    "postage.svg",
    "truck-front.svg",
    "truck.svg",
    "airplane-engines.svg",
  ];

  const iconCount = 3;
  const icons = [];
  const iconSize = 60; // px

  // Create icons with random positions and velocities
  iconNames.forEach((icon, i) => {
    for (let j = 0; j < iconCount; j++) {
      const img = document.createElement("img");
      img.src = `icons/${icon}`;
      img.className = `sprite icon-${i} instance-${j}`;
      // Random start position
      let x = Math.random() * (window.innerWidth - iconSize);
      let y = Math.random() * (window.innerHeight - iconSize);
      // Random velocity and direction
      let angle = Math.random() * 2 * Math.PI;
      let speed = 0.5 + Math.random() * 1.5; // px per frame
      let vx = Math.cos(angle) * speed;
      let vy = Math.sin(angle) * speed;
      img.style.left = `${x}px`;
      img.style.top = `${y}px`;
      bg.appendChild(img);
      icons.push({ img, x, y, vx, vy });
    }
  });

  // Animation loop
  function animateIcons() {
    const w = window.innerWidth;
    const h = window.innerHeight;
    icons.forEach((icon) => {
      icon.x += icon.vx;
      icon.y += icon.vy;

      // Bounce off left/right
      if (icon.x <= 0) {
        icon.x = 0;
        icon.vx = Math.abs(icon.vx);
      } else if (icon.x >= w - iconSize) {
        icon.x = w - iconSize;
        icon.vx = -Math.abs(icon.vx);
      }
      // Bounce off top/bottom
      if (icon.y <= 0) {
        icon.y = 0;
        icon.vy = Math.abs(icon.vy);
      } else if (icon.y >= h - iconSize) {
        icon.y = h - iconSize;
        icon.vy = -Math.abs(icon.vy);
      }

      icon.img.style.left = `${icon.x}px`;
      icon.img.style.top = `${icon.y}px`;
    });
    requestAnimationFrame(animateIcons);
  }
  animateIcons();

  // Optional: Recalculate bounds on resize
  window.addEventListener("resize", () => {
    icons.forEach((icon) => {
      icon.x = Math.min(icon.x, window.innerWidth - iconSize);
      icon.y = Math.min(icon.y, window.innerHeight - iconSize);
    });

    // Update slider positions on resize
    updateSliderPosition(timeSlider, timeThumb);
    updateSliderPosition(costSlider, costThumb);
    updateSliderPosition(emissionsSlider, emissionsThumb);
  });
});
