let commentCount = 0;

function prompt_model(comment) {
  // Stub for future backend call
  return Promise.resolve({ status: "success" });
}

async function solve_model(start, end) {
  return fetch("http://127.0.0.1:8000/api/solve", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ start, end }),
  }).then((res) => res.json());
}


document.addEventListener("DOMContentLoaded", () => {
  const bg = document.querySelector('.background');

  // ---- wire up your button ----
  const btn = document.getElementById("solve-model");
  btn.addEventListener("click", async () => {
    const start = document.getElementById("start").value.trim();
    const end   = document.getElementById("end").value.trim();
    if (!start || !end) {
      document.getElementById("output").textContent = "Please enter both addresses.";
      return;
    }
    try {
      const result = await solve_model(start, end);
      document.getElementById("output").textContent = JSON.stringify(result, null, 2);
    } catch (err) {
      document.getElementById("output").textContent = "Error contacting backend.";
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
  });
  
});

