// Initialize D3 visualization
const container = document.getElementById("bus-vis");
const width = container.clientWidth || 800;
const height = container.clientHeight || 300;
const margin = { top: 20, right: 20, bottom: 30, left: 50 };

const svg = d3.select("#bus-vis")
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

// Glow effect
const defs = svg.append("defs");
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
const y = d3.scaleStep().range([height - margin.top - margin.bottom, 0]);

// Axes
const xAxis = d3.axisBottom(x).ticks(20).tickFormat(d => d + "ms");
const yAxis = d3.axisLeft(y).ticks(2).tickFormat(d => d === 1 ? "REC (1)" : "DOM (0)");

svg.append("g")
    .attr("class", "x-axis")
    .attr("transform", `translate(0,${height - margin.top - margin.bottom})`)
    .call(xAxis)
    .style("color", "#45a29e")
    .style("font-family", "Share Tech Mono");

svg.append("g")
    .attr("class", "y-axis")
    .call(yAxis)
    .style("color", "#45a29e")
    .style("font-family", "Share Tech Mono");

// Grid lines
function make_x_gridlines() { return d3.axisBottom(x).ticks(20) }
function make_y_gridlines() { return d3.axisLeft(y).ticks(2) }

svg.append("g")
    .attr("class", "grid")
    .attr("transform", `translate(0,${height - margin.top - margin.bottom})`)
    .call(make_x_gridlines().tickSize(-(height - margin.top - margin.bottom)).tickFormat(""))
    .style("stroke", "#333")
    .style("stroke-opacity", "0.2");

svg.append("g")
    .attr("class", "grid")
    .call(make_y_gridlines().tickSize(-(width - margin.left - margin.right)).tickFormat(""))
    .style("stroke", "#333")
    .style("stroke-opacity", "0.2");

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
svg.append("path")
    .datum(data)
    .attr("fill", "none")
    .attr("stroke", "#66fcf1")
    .attr("stroke-width", 2)
    .attr("d", line)
    .style("filter", "url(#glow)");

// Add labels
svg.append("text")
    .attr("x", (width - margin.left - margin.right) / 2)
    .attr("y", -5)
    .style("text-anchor", "middle")
    .style("fill", "#66fcf1")
    .style("font-family", "Share Tech Mono")
    .style("text-shadow", "0 0 5px #66fcf1")
    .text("CAN BUS ARBITRATION TIMELINE");
