// Initialize D3 visualization
const container = document.getElementById("bus-vis");
const width = container.clientWidth || 800;
const height = container.clientHeight || 300;
const margin = { top: 20, right: 20, bottom: 30, left: 50 };

const svg = d3.select("#bus-vis")
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("role", "img")
    .attr("aria-label", "CAN Bus Arbitration Timeline Visualization")
    .attr("tabindex", "0");

// Accessibility: Provide semantic descriptions for screen readers
svg.append("title").text("CAN Bus Arbitration Simulation");
svg.append("desc").text("A logic analyzer timeline showing CAN bus arbitration. The Sun Sensor (ID 0x001) transmits its dominant priority bits and wins arbitration against the Camera (ID 0x100), which backs off and stops transmitting.");

const g = svg.append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

// Glow effect
const defs = g.append("defs");
const filter = defs.append("filter")
    .attr("id", "glow");

filter.append("feGaussianBlur")
    .attr("stdDeviation", "2.5")
    .attr("result", "coloredBlur");

const feMerge = filter.append("feMerge");
feMerge.append("feMergeNode").attr("in", "coloredBlur");
feMerge.append("feMergeNode").attr("in", "SourceGraphic");

// Scales
const x = d3.scaleLinear().range([0, width - margin.left - margin.right]);
const y = d3.scaleLinear().range([height - margin.top - margin.bottom, 0]);

// Axes
const xAxis = d3.axisBottom(x).ticks(20).tickFormat(d => d + "ms");
const yAxis = d3.axisLeft(y).ticks(2).tickFormat(d => d === 1 ? "REC (1)" : "DOM (0)");

g.append("g")
    .attr("class", "x-axis axis-label")
    .attr("transform", `translate(0,${height - margin.top - margin.bottom})`)
    .call(xAxis);

g.append("g")
    .attr("class", "y-axis axis-label")
    .call(yAxis);

// Grid lines
function make_x_gridlines() { return d3.axisBottom(x).ticks(20) }
function make_y_gridlines() { return d3.axisLeft(y).ticks(2) }

g.append("g")
    .attr("class", "grid grid-line")
    .attr("transform", `translate(0,${height - margin.top - margin.bottom})`)
    .call(make_x_gridlines().tickSize(-(height - margin.top - margin.bottom)).tickFormat(""));

g.append("g")
    .attr("class", "grid grid-line")
    .call(make_y_gridlines().tickSize(-(width - margin.left - margin.right)).tickFormat(""));

// Data generator (Same logic, better structure)
function generateBusData() {
    const data = [];
    let currentTime = 0;

    // Helper to push state
    const push = (val, duration) => {
        data.push({ time: currentTime, signal: val });
        currentTime += duration;
        data.push({ time: currentTime, signal: val }); // Hold value
    };

    push(1, 10); // Idle
    push(0, 10); // Start
    push(0, 10); // Arb 1
    push(0, 10); // Arb 2
    push(0, 10); // Arb 3 (Cam backs off)

    // Rest of ID 0x001 (0000001)
    push(0, 10);
    push(0, 10);
    push(0, 10);
    push(0, 10);
    push(0, 10);
    push(0, 10);
    push(1, 10);

    push(1, 20); // Idle

    return data;
}

const data = generateBusData();

// Update domains
x.domain([0, d3.max(data, d => d.time)]);
y.domain([0, 1]);

// Line generator
const line = d3.line()
    .curve(d3.curveStepAfter)
    .x(d => x(d.time))
    .y(d => y(d.signal));

// Add path with glow
g.append("path")
    .datum(data)
    .attr("class", "bus-path")
    .attr("d", line);

// Add labels
g.append("text")
    .attr("class", "bus-title")
    .attr("x", (width - margin.left - margin.right) / 2)
    .attr("y", -5)
    .text("CAN BUS ARBITRATION TIMELINE");
