// 2. Use the margin convention practice 
var margin = { top: 50, right: 50, bottom: 50, left: 50 }
    , width = window.innerWidth/3 - margin.left - margin.right // Use the window's width 
    , height = window.innerHeight/3.5 - margin.top - margin.bottom; // Use the window's height


var color_tev = ['#993404', '#D95F0E', '#FE9929', '#FEE391', '#FFFFD4'];

var color_v03 = ['rgb(0, 204, 102)', '#2d9f13', '#06763b' ,'pink','rgb(92,5,88)']

// var color_prs = ['#ffffcc', '#a1dab4', '#41b6c4', '#2c7fb8', '#253494'];


var color_prs = ["rgb(3,4, 94)", "rgb(0, 119, 182)", "rgb(0, 180 , 216)", "rgb(144, 224, 239)", "rgb(202, 240, 248)"]
var color = "grey"
var v02_color = [color, color, color, color, color]
// var color_prs = ["#ca0020", "#f4a582", "#f7f7f7", "#92c5de", "#0571b0"];


var colorranges = [color_tev, color_v03, color_prs, color_tev, color_v03, v02_color];
var csvs = ["tev", "v03", "prs_max", "tev_max", "v03_max", "v02_splash"]
var names = ["tev", "v03", "prs", "tev", "v03", "x"]
var ttles = ['Mean Temperature (eV)', "Mean Asteroid volume", "Max Pressure (µbar)",  
    'Max Temperature (eV)', "Max Asteroid volume", "Max water splash height (m)"]
var title = ['Temperature (eV)', "Asteroid volume", "Pressure (µbar)"];

var seconds = [0.1141, 0.2286, 0.4566, 0.6817, 0.8948, 1.0487, 1.2244, 1.3306, 1.5159, 1.6898, 1.7954, 1.8741, 1.9021, 1.9749, 2.055, 2.201, 2.3341, 2.4095, 2.5659, 2.6103, 2.797, 2.8245, 2.9693, 3.0068, 3.3719, 3.5332, 3.6069, 3.7669, 3.9067, 4.1035, 4.4262, 4.6984, 4.8989, 4.9275, 4.9577, 4.9978]


var n = 36;
var xScale = d3.scaleLinear()
    .domain([Math.min.apply(Math, seconds.map(function (o) { return o })),
    Math.max.apply(Math, seconds.map(function (o) { return o }))]) // input 
    .range([0, width]); // output

for (let i = 0; i < csvs.length; i++) {
    

    d3.csv("cvlibd/server/data/volume-render/" + csvs[i] + ".csv",
        function(dataset) {
            
            var yScale = d3.scaleLinear()
                .domain([Math.min.apply(Math, dataset.map(function (o) { return o[names[i]]; })),
                    Math.max.apply(Math, dataset.map(function (o) { return o[names[i]]; }))]) // input 
                .range([height, 0]); // output 
            var logScale = d3.scaleLog()
                .domain([Math.min.apply(Math, dataset.map(function (o) { return o[names[i]] ; })),
                Math.max.apply(Math, dataset.map(function (o) { return o[names[i]]; }))]) // input 
                .range([height, 0]); // output 


            var line = d3.line()
                .x(function (d, i) { return xScale(seconds[i]); }) // set the x values for the line generator
                .y(function (d) { return yScale(d[names[i]]); }) // set the y values for the line generator 
                .curve(d3.curveBasis) // apply smoothing to the line
            var logline = d3.line()
                .x(function (d, i) { return xScale(seconds[i]); }) // set the x values for the line generator
                .y(function (d) { return logScale(d[names[i]]); }) // set the y values for the line generator 
                .curve(d3.curveBasis) // apply smoothing to the line

            // 1. Add the SVG to the page and employ #2
            var svg = d3.select("#" + csvs[i]).append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom + 10)
                .append("g")
                .attr("class", "svg")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

            // 3. Call the x axis in a group tag
            svg.append("g")
                .attr("class", "x axis")
                .attr("transform", "translate(0," + height + ")")
                .call(d3.axisBottom(xScale).ticks(5)); // Create an axis component with d3.axisBottom
           
            svg.append("text")
                .attr("transform", "translate(" + (width) + "," + (height + 35) + ")")
                .text("Time (s)")
                .attr("text-anchor", "end")
                .attr("class", "axislabel")

            if (names[i] != "prs") {
            // 4. Call the y axis in a group tag
            svg.append("g")
                .attr("class", "y axis")
                .call(d3.axisLeft(yScale).tickFormat(function (d) {
                    if (i > 2 || i > 5)
                    {  return d3.format(".2f")(d / 1);}
                    else { return d3.format(".1f")(d* 100); }
                })); // Create an axis component with d3.axisLeft

                // 9. Append the path, bind the data, and call the line generator 
                svg.append("path")
                    .data(dataset)
                    .attr("class", "line") // Assign a class for styling 
                    .attr("d", line); // 11. Calls the line generator 
            }
            else {
                svg.append("g")
                    .attr("class", "y axis")
                    .call(d3.axisLeft(logScale).ticks(6)); // Create an axis component with d3.axisLeft

                // 9. Append the path, bind the data, and call the line generator 
                svg.append("path")
                    .data(dataset)
                    .attr("class", "line") // Assign a class for styling 
                    .attr("d", logline); // 11. Calls the line generator 
            }       
            
            svg.append("text")
                .text(ttles[i])
                .style("fill", "white")
                .attr("transform", "translate(10, -10)")

        

            var color = d3.scaleLinear().range(colorranges[i]).domain([1, 2, 3, 4, 5]);

            var x = d3.scaleLinear().range([0, width]);
            var y = d3.scaleLinear().range([height, 0]);

            x.domain(d3.extent(dataset, function (d, i) { return i; }));
            y.domain(d3.extent(dataset, function (d) { return d[names[i]]; }));

            var linearGradient = svg.append("defs")
                .append("linearGradient")
                .attr("id", "linear-gradient" + i)
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

            if (names[i] == "prs") {
                svg.append("path")
                    .attr("d", logline(dataset))
                    .attr("stroke-width", 4)
                    .attr("stroke", "url(#linear-gradient" + i + ")")
                    .attr("fill", "none");
            }
            else {
                svg.append("path")
                    .attr("d", line(dataset))
                    .attr("stroke-width", 4)
                    .attr("stroke", "url(#linear-gradient" + i + ")")
                    .attr("fill", "none");
            }
            
            svg.append("line")
                .attr("x1", 0)
                .attr("y1", margin.top)
                .attr("x2", 0)
                .attr("y2", height - window.innerHeight / 3)
                .attr("class", "timestep")
                .style("stroke-width", 1)
                .style("stroke", "black")
                .style("fill", "none");
            
            if (i < 3) {
                var key = d3.select("#legends")
                    .append("svg")
                    .attr("width", 280)
                    .attr("transform", "translate(-25, 0)")
                    .attr("height", 100);
                    
                var legend = key.append("defs")
                    .append("linearGradient")
                    .attr("id", "linear-gradients" + i)
                    .attr("spreadMethod", "pad");

                legend.append("stop")
                    .attr("offset", "0%")
                    .attr("stop-opacity", 1)
                    .attr("stop-color", color(5));

                legend.append("stop")
                    .attr("offset", "25%")
                    .attr("stop-color", color(4));

                legend.append("stop")
                    .attr("offset", "50%")
                    .attr("stop-color", color(3));

                legend.append("stop")
                    .attr("offset", "75%")
                    .attr("stop-color", color(2));

                legend.append("stop")
                    .attr("offset", "100%")
                    .attr("stop-color", color(1));

                key.append("rect")
                    .attr("width", "100%")
                    .attr("height", 18)
                    .style("fill", "url(#linear-gradients" + i + ")")
                    .attr("transform", "translate(0, 25)");

                key.append("g")
                    .attr("transform", "translate(0,52)")
                    .call(x)
                    .append("text")
                    .attr("y", 0)
                    .attr("dy", ".71em")
                    .style("fill", "white")
                    .text(getNotation("min"));
                key.append("g")
                    .attr("transform", "translate(275,52)")
                    .call(x)
                    .append("text")
                    .attr("y", 0)
                    .attr("dy", ".71em")
                    .style("fill", "white")
                    .style("text-anchor", "end")
                    .text(getNotation("max"));

                key.append("g")
                    .attr("transform", "translate(5,0)")
                    .call(x)
                    .append("text")
                    .attr("y", 0)
                    .attr("dy", ".71em")
                    .style("fill", "white")
                    .text(title[i]);
            }

            function getNotation(minmax) {
                if (names[i] == "prs") {
                    if (minmax == "min") {
                        return Math.round(Math.min.apply(Math, dataset.map(function (o) { return o[names[i]]; }))
                            , 3).toExponential(1)
                    }
                    else {
                        return Math.round(Math.max.apply(Math, dataset.map(function (o) { return o[names[i]]; }))
                            , 3).toExponential(1)
                    }
                }
                else {
                    if (minmax == "max") {
                        return Math.round(Math.max.apply(Math, dataset.map(function (o) { return o[names[i]]; })) * 1000) / 10;
                    }
                    else {
                        return Math.round(Math.min.apply(Math, dataset.map(function (o) { return o[names[i]]; })) * 1000) / 10;
                    }   
                }
            }

    });
}

function updateLine(select) {
    d3.selectAll(".timestep")
        .attr("x1", xScale(seconds[select]))
        .attr("y1", height )
        .attr("x2", xScale(seconds[select]))
        .attr("y2", 0)
        .attr("class", "timestep")
        .style("stroke-width", 3.5)
        .style("stroke", "rgb(50, 50, 70)")
        .style("fill", "none");
}

