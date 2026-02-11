// Initialize D3 visualization
const width = 600;
const height = 200;
const margin = { top: 20, right: 20, bottom: 30, left: 50 };

const svg = d3.select("#bus-vis")
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

// Scales
const x = d3.scaleLinear().range([0, width]);
const y = d3.scaleStep().range([height, 0]);

// Axes
const xAxis = d3.axisBottom(x);
const yAxis = d3.axisLeft(y).ticks(2);

svg.append("g")
    .attr("class", "x-axis")
    .attr("transform", `translate(0,${height})`)
    .call(xAxis);

svg.append("g")
    .attr("class", "y-axis")
    .call(yAxis);

// Data generator
function generateBusData() {
    const data = [];
    let currentTime = 0;

    // Idle
    data.push({ time: currentTime, signal: 1 });
    currentTime += 10;

    // Start bit (0)
    data.push({ time: currentTime, signal: 0 });
    currentTime += 10;

    // Arbitration: Sun Sensor (0x001) wins against Camera (0x100)
    // 0x001: 000 0000 0001
    // 0x100: 001 0000 0000

    // Bit 10: Both 0
    data.push({ time: currentTime, signal: 0 });
    currentTime += 10;

    // Bit 9: Both 0
    data.push({ time: currentTime, signal: 0 });
    currentTime += 10;

    // Bit 8: Sun(0), Cam(1). Bus goes 0. Cam backs off.
    data.push({ time: currentTime, signal: 0 });
    currentTime += 10;

    // Rest of Sun Sensor ID (0000001)
    for (let i = 0; i < 7; i++) {
        let bit = (0x001 >> (7-1-i)) & 1;
        data.push({ time: currentTime, signal: bit });
        currentTime += 10;
    }

    // Idle
    data.push({ time: currentTime, signal: 1 });

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

// Add path
svg.append("path")
    .datum(data)
    .attr("fill", "none")
    .attr("stroke", "#00ff00")
    .attr("stroke-width", 2)
    .attr("d", line);

// Add labels
svg.append("text")
    .attr("x", width / 2)
    .attr("y", -5)
    .style("text-anchor", "middle")
    .style("fill", "#ccc")
    .text("CAN Bus Arbitration (Sun Sensor vs Camera)");
