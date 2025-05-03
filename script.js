let commentCount = 0;
let map = null;
let startMarker = null;
let endMarker = null;

function prompt_model(comment) {
  // Stub for future backend call
  return Promise.resolve({ status: "success" });
}

async function solve_model(start, end, preferences) {
  try {
    const response = await fetch("http://127.0.0.1:8000/api/solve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        start,
        end,
        preferences,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log("Backend response:", data); // Debug log
    return data;
  } catch (error) {
    console.error("Error in solve_model:", error); // Debug log
    throw error;
  }
}

function initMap() {
  try {
    console.log("Initializing map..."); // Debug log

    // Initialize map centered on the US
    map = L.map("map").setView([39.8283, -98.5795], 4);
    console.log("Map initialized:", map); // Debug log

    // Add OpenStreetMap tiles
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "© OpenStreetMap contributors",
    }).addTo(map);

    console.log("Tile layer added"); // Debug log
  } catch (error) {
    console.error("Error initializing map:", error); // Debug log
    throw error;
  }
}

// Colors for different transport modes
const TRANSPORT_COLORS = {
  road: "#4CAF50", // Green
  train: "#2196F3", // Blue
  boat: "#9C27B0", // Purple
  airplane: "#FF9800", // Orange
};

function drawRoute(route) {
  console.log("Drawing route:", route); // Debug log

  // Clear any existing route
  if (window.routeLayer) {
    map.removeLayer(window.routeLayer);
  }

  // Create a new layer group for the route
  window.routeLayer = L.layerGroup();
  map.addLayer(window.routeLayer);

  // Draw each segment of the route
  route.forEach((segment, index) => {
    console.log("Drawing segment:", segment); // Debug log
    const { from, to, mode } = segment;
    const color = TRANSPORT_COLORS[mode] || "#000000";

    // Create a line between the points
    const latlngs = [
      [from.coords[0], from.coords[1]],
      [to.coords[0], to.coords[1]],
    ];

    try {
      // Create a straight line
      const line = L.polyline(latlngs, {
        color: color,
        weight: 5,
        opacity: 0.7,
        dashArray: mode === "airplane" ? "10, 10" : undefined,
        className: `route-segment-${mode}`,
      });
      line.addTo(window.routeLayer);

      // Add a small circle at the start of each segment (except first)
      if (index > 0) {
        const circle = L.circleMarker(latlngs[0], {
          radius: 5,
          fillColor: color,
          color: "#fff",
          weight: 1,
          opacity: 1,
          fillOpacity: 0.7,
        });
        circle.addTo(window.routeLayer);
      }
    } catch (error) {
      console.error("Error drawing route segment:", error);
    }
  });

  // Get all the layers in the route layer group
  const layers = window.routeLayer.getLayers();
  if (layers.length > 0) {
    // Create a bounds object that includes all the layers
    const bounds = L.latLngBounds([]);
    layers.forEach((layer) => {
      if (layer.getLatLngs) {
        // For polylines
        const latlngs = layer.getLatLngs();
        latlngs.forEach((latlng) => bounds.extend(latlng));
      } else if (layer.getLatLng) {
        // For markers and circles
        bounds.extend(layer.getLatLng());
      }
    });
    // Fit the map to show all the layers
    map.fitBounds(bounds, { padding: [50, 50] });
  }
}

// Modify the existing updateMap function to handle routes
function updateMap(startCoords, endCoords, route = null) {
  // Clear existing markers and route
  if (startMarker) map.removeLayer(startMarker);
  if (endMarker) map.removeLayer(endMarker);
  if (window.routeLayer) map.removeLayer(window.routeLayer);

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

  // Draw route if provided
  if (route) {
    drawRoute(route);
  } else {
    // Fit map to show both markers
    const bounds = L.latLngBounds([
      startMarker.getLatLng(),
      endMarker.getLatLng(),
    ]);
    map.fitBounds(bounds, { padding: [50, 50] });
  }
}

// Add this function after the TRANSPORT_COLORS constant
function createTransportIcon(mode) {
  const iconMap = {
    road: "🚗",
    train: "🚂",
    boat: "🚢",
    airplane: "✈️",
  };
  return iconMap[mode] || "➡️";
}

function createRouteVisualization(route, start, end) {
  const container = document.createElement("div");
  container.className = "route-visualization";

  // Create start city box
  const startBox = document.createElement("div");
  startBox.className = "city-box";
  startBox.textContent = start;
  container.appendChild(startBox);

  // Create route segments
  route.forEach((segment, index) => {
    // Create transport arrow
    const arrow = document.createElement("div");
    arrow.className = "transport-arrow";
    arrow.textContent = createTransportIcon(segment.mode);
    container.appendChild(arrow);

    // Create city box
    const cityBox = document.createElement("div");
    cityBox.className = "city-box";
    cityBox.textContent = index === route.length - 1 ? end : segment.to.name;
    container.appendChild(cityBox);
  });

  return container;
}

function createCostHistogram(costs, title) {
  const container = document.createElement("div");
  container.className = "cost-histogram";

  const canvas = document.createElement("canvas");
  container.appendChild(canvas);

  const ctx = canvas.getContext("2d");
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Time (hours)", "Cost ($)", "Emissions (kg)", "Total"],
      datasets: [
        {
          label: title,
          data: [costs.time, costs.cost, costs.emissions, costs.total],
          backgroundColor: [
            "rgba(255, 99, 132, 0.5)",
            "rgba(54, 162, 235, 0.5)",
            "rgba(75, 192, 192, 0.5)",
            "rgba(153, 102, 255, 0.5)",
          ],
          borderColor: [
            "rgba(255, 99, 132, 1)",
            "rgba(54, 162, 235, 1)",
            "rgba(75, 192, 192, 1)",
            "rgba(153, 102, 255, 1)",
          ],
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function (value) {
              return value.toFixed(2);
            },
          },
        },
      },
      plugins: {
        tooltip: {
          callbacks: {
            label: function (context) {
              return context.dataset.label + ": " + context.raw.toFixed(2);
            },
          },
        },
      },
    },
  });

  return container;
}

function createCostVisualization(costs) {
  const container = document.createElement("div");
  container.className = "cost-visualization";

  // Create a row for the current preferences
  const currentRow = document.createElement("div");
  currentRow.className = "cost-row";
  currentRow.appendChild(
    createCostHistogram(costs.current, "Current Preferences")
  );
  container.appendChild(currentRow);

  // Create a row for the three extreme cases
  const extremesRow = document.createElement("div");
  extremesRow.className = "cost-row";
  extremesRow.appendChild(
    createCostHistogram(costs.time_optimized, "Time Optimized")
  );
  extremesRow.appendChild(
    createCostHistogram(costs.cost_optimized, "Cost Optimized")
  );
  extremesRow.appendChild(
    createCostHistogram(costs.emissions_optimized, "Emissions Optimized")
  );
  container.appendChild(extremesRow);

  return container;
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

      // Update map with coordinates and route if available
      if (result.coords_start && result.coords_end) {
        updateMap(result.coords_start, result.coords_end, result.route);

        // Clear previous output
        const outputDiv = document.getElementById("output");
        outputDiv.innerHTML = "";

        // Create and add route visualization
        if (result.route && result.route.length > 0) {
          const visualization = createRouteVisualization(
            result.route,
            start,
            end
          );
          outputDiv.appendChild(visualization);

          // Add cost visualization if available
          if (result.costs) {
            const costVisualization = createCostVisualization(result.costs);
            outputDiv.appendChild(costVisualization);
          }
        } else {
          outputDiv.textContent = "No route segments found.";
        }
      } else {
        document.getElementById("output").textContent =
          "No route data received from backend.";
      }
    } catch (err) {
      console.error("Error:", err);
      document.getElementById("output").textContent =
        "Error contacting backend: " + err.message;
    }
  });

  // Send comment functionality
  const sendCommentBtn = document.getElementById("send");
  const commentInput = document.getElementById("comment");
  const commentsContainer = document.getElementById("comments");

  sendCommentBtn.addEventListener("click", async () => {
    const commentText = commentInput.value.trim();
    if (commentText) {
      try {
        // Send comment to backend
        const response = await fetch("http://127.0.0.1:8000/api/comment", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ comment: commentText }),
        });

        const result = await response.json();

        // Create and add comment pill
        const commentPill = document.createElement("div");
        commentPill.className = "comment-pill";
        commentPill.textContent = commentText;
        commentsContainer.appendChild(commentPill);
        commentInput.value = "";

        // Log the response from the backend
        console.log("Backend response:", result);
      } catch (err) {
        console.error("Error sending comment:", err);
        // Still show the comment even if backend call fails
        const commentPill = document.createElement("div");
        commentPill.className = "comment-pill";
        commentPill.textContent = commentText;
        commentsContainer.appendChild(commentPill);
        commentInput.value = "";
      }
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

  const iconCount = 8;
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
