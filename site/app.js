
// Simple interactive swimlane using D3
// Expects data: { lanes: {Leader: [{name, ms}], Network: [...], Follower: [...], Video: [...]}, totals: {...}, overall: number }

const scenarios = ["Best", "Typical", "Worst"]; // can add Selected later if needed

async function loadData(scenario) {
  const resp = await fetch(`data/latency_${scenario}.json`);
  if (!resp.ok) throw new Error("Failed to load data for " + scenario);
  return await resp.json();
}

function render(data) {
  const container = d3.select("#diagram");
  container.selectAll("*").remove();

  const lanes = Object.keys(data.lanes);
  const laneWidth = 320;
  const laneGap = 40;
  const stepHeight = 62;
  const headerHeight = 40;
  const padding = 20;

  const maxSteps = d3.max(lanes.map(l => data.lanes[l].length));
  const width = padding*2 + lanes.length * (laneWidth + laneGap) - laneGap;
  const height = padding*2 + maxSteps * stepHeight + headerHeight + 60;

  const svg = container.append("svg")
    .attr("width", width)
    .attr("height", height);

  const g = svg.append("g").attr("transform", `translate(${padding},${padding})`);

  // Title with overall total
  svg.append("text")
    .attr("x", width/2).attr("y", 18)
    .attr("text-anchor", "middle")
    .attr("font-size", "16px").attr("font-weight", "600")
    .text(`Overall Command→Photon: ${data.overall.toFixed(1)} ms`);

  // Tooltip
  const tooltip = d3.select("body").append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);

  // Draw lanes
  lanes.forEach((lane, li) => {
    const x = li * (laneWidth + laneGap);
    const y = 30;

    // Lane background
    g.append("rect")
      .attr("x", x).attr("y", y)
      .attr("width", laneWidth).attr("height", maxSteps * stepHeight + headerHeight)
      .attr("fill", "#f0f0f0").attr("rx", 10);

    // Header with toggle
    const header = g.append("g").attr("transform", `translate(${x+10},${y+24})`);
    const laneState = { collapsed: false };

    header.append("text")
      .attr("class", "lane-title")
      .text(`${lane} (total ${data.totals[lane].toFixed(1)} ms)`)
      .style("cursor", "pointer")
      .on("click", () => {
        laneState.collapsed = !laneState.collapsed;
        stepsGroup.style("display", laneState.collapsed ? "none" : null);
      });

    // Steps
    const stepsGroup = g.append("g").attr("transform", `translate(${x+10},${y+headerHeight})`);
    const steps = data.lanes[lane];

    steps.forEach((s, i) => {
      const gy = i * stepHeight;
      // Step box
      stepsGroup.append("rect")
        .attr("x", 0).attr("y", gy)
        .attr("width", laneWidth-20).attr("height", stepHeight-10)
        .attr("rx", 8)
        .attr("fill", s.color || "white")
        .attr("stroke", "#999")
        .on("mouseover", (event) => {
          tooltip.transition().duration(150).style("opacity", 0.95);
          tooltip.html(`<strong>${s.name}</strong><br>${s.ms.toFixed(1)} ms`)
            .style("left", (event.pageX + 12) + "px")
            .style("top", (event.pageY + 12) + "px");
        })
        .on("mouseout", () => tooltip.transition().duration(150).style("opacity", 0));

      // Step labels
      stepsGroup.append("text")
        .attr("x", 12).attr("y", gy + 22)
        .attr("class", "step-name")
        .text(s.name);

      stepsGroup.append("text")
        .attr("x", laneWidth - 32).attr("y", gy + 22)
        .attr("text-anchor", "end")
        .attr("class", "step-ms")
        .text(`${s.ms.toFixed(1)} ms`);
    });

    // Connectors (simple arrows between steps)
    steps.forEach((s, i) => {
      if (i < steps.length - 1) {
        const y1 = y + headerHeight + (i * stepHeight) + (stepHeight/2) - 5;
        const y2 = y + headerHeight + ((i+1) * stepHeight) + (stepHeight/2) - 5;
        g.append("line")
          .attr("x1", x + laneWidth - 10)
          .attr("y1", y1)
          .attr("x2", x + laneWidth - 10)
          .attr("y2", y2)
          .attr("stroke", "#bbb").attr("marker-end", "url(#arrow)");
      }
    });
  });

  // Define arrow marker
  svg.append("defs").append("marker")
    .attr("id", "arrow")
    .attr("markerWidth", 10).attr("markerHeight", 10)
    .attr("refX", 6).attr("refY", 3)
    .attr("orient", "auto")
    .append("path").attr("d", "M0,0 L0,6 L6,3 z").attr("fill", "#bbb");
}

function applyScenario(scenario) {
  loadData(scenario).then(data => {
    render(data);
    document.getElementById("currentScenario").innerText = scenario;
  }).catch(err => {
    console.error(err);
    d3.select("#diagram").html(`<div class="error">Failed to load data: ${err}</div>`);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const sel = document.getElementById("scenario");
  scenarios.forEach(s => {
    const opt = document.createElement("option");
    opt.value = s; opt.textContent = s;
    sel.appendChild(opt);
  });
  sel.value = "Typical";
  sel.addEventListener("change", () => applyScenario(sel.value));

  applyScenario("Typical");
});
