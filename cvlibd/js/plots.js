// 2. Use the margin convention practice 
var margin = { top: 50, right: 50, bottom: 50, left: 50 }
    , width = window.innerWidth/3 - margin.left - margin.right // Use the window's width 
    , height = window.innerHeight/3 - margin.top - margin.bottom; // Use the window's height


var color_tev = ['#993404', '#D95F0E', '#FE9929', '#FEE391', '#FFFFD4'];

var color_v03 = ['rgb(0, 204, 102)', '#2d9f13', '#06763b' ,'pink','rgb(92,5,88)']

// var color_prs = ['#ffffcc', '#a1dab4', '#41b6c4', '#2c7fb8', '#253494'];

var color_prs = ["#ca0020", "#f4a582", "#f7f7f7", "#92c5de", "#0571b0"];


var colorranges = [color_tev, color_v03, color_prs, color_tev, color_v03, color_prs];
var csvs = ["tev_max", "v03_max", "prs_max", "tev", "v03", "prs"]
var names = ["tev", "v03", "prs", "tev", "v03", "prs"]
var ttles = ['Max Temperature (eV)', "Max Asteroid volume", "Max Pressure (µbar)", 
            'Mean Temperature (eV)', "Asteroid mean volume", "Mean Pressure (µbar)"]

var n = 36;
var xScale = d3.scaleLinear()
    .domain([0, n - 1]) // input
    .range([0, width]); // output

for (let i = 0; i < csvs.length; i++) {
    

    d3.csv("cvlibd/server/data/volume-render/" + csvs[i] + ".csv",
        function(dataset) {
            
            var margin_bottom = 0;
            var yScale = d3.scaleLinear()
                .domain([Math.min.apply(Math, dataset.map(function (o) { return o[names[i]] - margin_bottom; })),
                    Math.max.apply(Math, dataset.map(function (o) { return o[names[i]]; }))]) // input 
                .range([height, 0]); // output 


            var line = d3.line()
                .x(function (d, i) { return xScale(i); }) // set the x values for the line generator
                .y(function (d) { return yScale(d[names[i]]); }) // set the y values for the line generator 
                .curve(d3.curveBasis) // apply smoothing to the line

            // 1. Add the SVG to the page and employ #2
            var svg = d3.select("#" + csvs[i]).append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
                .append("g")
                .attr("class", "svg")
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
                .data(dataset) 
                .attr("class", "line") // Assign a class for styling 
                .attr("d", line); // 11. Calls the line generator 

            if (i > 2)
            {
                svg.append("text")
                    .text(ttles[i])
                    .style("fill", "white")
                    .attr("transform", "translate(10, 20)")
            }
            else {
                svg.append("text")
                    .text(ttles[i])
                    .style("fill", "white")
                    .attr("transform", "translate(10, -10)")
            }

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
    
            svg.append("path")
                .attr("d", line(dataset))
                .attr("stroke-width", 4)
                .attr("stroke", "url(#linear-gradient" + i + ")")
                .attr("fill", "none");
            
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
                    .attr("width", 200)
                    .attr("height", 80);
                    
                var legend = key.append("defs")
                    .append("linearGradient")
                    .attr("id", "linear-gradients" + i)
                    .attr("spreadMethod", "pad");

                legend.append("stop")
                    .attr("offset", "0%")
                    .attr("stop-opacity", 1)
                    .attr("stop-color", color(1));

                legend.append("stop")
                    .attr("offset", "25%")
                    .attr("stop-color", color(2));

                legend.append("stop")
                    .attr("offset", "50%")
                    .attr("stop-color", color(3));

                legend.append("stop")
                    .attr("offset", "75%")
                    .attr("stop-color", color(4));

                legend.append("stop")
                    .attr("offset", "100%")
                    .attr("stop-color", color(5));

                key.append("rect")
                    .attr("width", "100%")
                    .attr("height", 18)
                    .style("fill", "url(#linear-gradients" + i + ")")
                    .attr("transform", "translate(0, 25)");

                key.append("g")
                    .attr("transform", "translate(5,0)")
                    .call(x)
                    .append("text")
                    .attr("y", 0)
                    .attr("dy", ".71em")
                    .style("fill", "white")
                    .text(ttles[i]);
            }

    });
}

function updateLine(select) {
    d3.selectAll(".timestep")
        .attr("x1", xScale(select))
        .attr("y1", height )
        .attr("x2", xScale(select))
        .attr("y2", 0)
        .attr("class", "timestep")
        .style("stroke-width", 3.5)
        .style("stroke", "rgb(50, 50, 70)")
        .style("fill", "none");
}

