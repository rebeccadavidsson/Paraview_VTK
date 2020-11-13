// 2. Use the margin convention practice 
var margin = { top: 50, right: 50, bottom: 50, left: 50 }
    , width = window.innerWidth/2.5 - margin.left - margin.right // Use the window's width 
    , height = window.innerHeight/2.5 - margin.top - margin.bottom; // Use the window's height

// The number of datapoints
var n = 21;

// 5. X scale will use the index of our data
var xScale = d3.scaleLinear()
    .domain([0, n - 1]) // input
    .range([0, width]); // output

// 6. Y scale will use the randomly generate number 
var yScale = d3.scaleLinear()
    .domain([0, 1]) // input 
    .range([height, 0]); // output 

// 7. d3's line generator
var line = d3.line()
    .x(function (d, i) { return xScale(i); }) // set the x values for the line generator
    .y(function (d) { return yScale(d.temperature); }) // set the y values for the line generator 
    .curve(d3.curveMonotoneX) // apply smoothing to the line

d3.csv("cvlibd/server/data/volume-render/temperature.csv",
    function(dataset) {

        // 1. Add the SVG to the page and employ #2
        var svg = d3.select("#temperatures").append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        // 3. Call the x axis in a group tag
        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")")
            .call(d3.axisBottom(xScale)); // Create an axis component with d3.axisBottom

        // 4. Call the y axis in a group tag
        svg.append("g")
            .attr("class", "y axis")
            .call(d3.axisLeft(yScale)); // Create an axis component with d3.axisLeft

        // 9. Append the path, bind the data, and call the line generator 
        svg.append("path")
            .datum(dataset) // 10. Binds data to the line 
            .attr("class", "line") // Assign a class for styling 
            .attr("d", line); // 11. Calls the line generator 

        // colorTransferFunction.AddRGBPoint(dMin, 255 / 255, 255 / 255, 212 / 255) # light yellow
        // colorTransferFunction.AddRGBPoint((dMax + dMin) / 5, 254 / 255, 227 / 255, 145 / 255)
        // colorTransferFunction.AddRGBPoint((dMax + dMin) / 4, 254 / 255, 196 / 255, 79 / 255)
        // colorTransferFunction.AddRGBPoint((dMax + dMin) / 3, 254 / 255, 153 / 255, 41 / 255)
        // colorTransferFunction.AddRGBPoint((dMax + dMin) / 2, 217 / 255, 95 / 255, 14 / 255)
        // colorTransferFunction.AddRGBPoint((dMax + dMin), 153 / 255, 52 / 255, 4 / 255)

        // var colorRange = ['#FFFFD4', '#FEE391', '#FE9929', '#D95F0E', '#993404'] //['#ffffcc', '#a1dab4', '#41b6c4', '#2c7fb8', '#253494']
        var colorRange = ['#993404', '#D95F0E', '#FE9929', '#FEE391', '#FFFFD4']
        var color = d3.scaleLinear().range(colorRange).domain([1, 2, 3, 4, 5]);

        var data = dataset;

        var x = d3.scaleLinear().range([0, width]);
        var y = d3.scaleLinear().range([height, 0]);

        x.domain(d3.extent(data, function (d, i) { return i; }));
        y.domain(d3.extent(data, function (d) { return d.temperature; }));

        var line = d3.line()
            .x(function (d, i) { return x(i); })
            .y(function (d) { return y(d.temperature); })
            .curve(d3.curveCardinal);


        var linearGradient = svg.append("defs")
            .append("linearGradient")
            .attr("id", "linear-gradient")
            .attr("gradientTransform", "rotate(90)");

        linearGradient.append("stop")
            .attr("offset", "0%")
            .attr("stop-color", color(1));

        linearGradient.append("stop")
            .attr("offset", "25%")
            .attr("stop-color", color(2));

        linearGradient.append("stop")
            .attr("offset", "50%")
            .attr("stop-color", color(3));

        linearGradient.append("stop")
            .attr("offset", "75%")
            .attr("stop-color", color(4));

        linearGradient.append("stop")
            .attr("offset", "100%")
            .attr("stop-color", color(5));


        svg.append("path")
            .attr("d", line(dataset))
            .attr("stroke-width", 6)
            .attr("stroke", "url(#linear-gradient)")
            .attr("fill", "none");






        // 1. Add the SVG to the page and employ #2
        var svg = d3.select("#v02").append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
        var linearGradient = svg.append("defs")
            .append("linearGradient")
            .attr("id", "linear-gradient")
            .attr("gradientTransform", "rotate(90)");

        linearGradient.append("stop")
            .attr("offset", "0%")
            .attr("stop-color", color(1));

        linearGradient.append("stop")
            .attr("offset", "25%")
            .attr("stop-color", color(2));

        linearGradient.append("stop")
            .attr("offset", "50%")
            .attr("stop-color", color(3));

        linearGradient.append("stop")
            .attr("offset", "75%")
            .attr("stop-color", color(4));

        linearGradient.append("stop")
            .attr("offset", "100%")
            .attr("stop-color", color(5));


        svg.append("path")
            .attr("d", line(dataset))
            .attr("stroke-width", 6)
            .attr("stroke", "url(#linear-gradient)")
            .attr("fill", "none");
    });

// });
