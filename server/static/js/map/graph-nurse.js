
nodes = {};

var svg;

function updateGraph(floor, client) {
    let baseUrl = "/graph";

    $.ajax({
        url: '/graph', // 服务器端的URL
        type: 'POST', // 请求类型，GET、POST、PUT等
        contentType: 'application/json', // 发送数据的格式
        data: JSON.stringify({
            'nurse': true
        }), // 将数据转换为JSON字符串
        success: function (args) {
            var nodeRadius = 5, linkStrokeWidth = 1;
            warnings = args.warnings;
            infusings = args.infusings;
            nodes = [...warnings, ...infusings].reduce((acc, current) => {
                acc[current.client] = current.pos
                return acc
            }, {});
            geojsonData = args.obstacle;
            console.log(args)
            // 清空图容器
            d3.select("#graph-container").selectAll("*").remove();
            geojsonData = JSON.parse(geojsonData)
            var width = $("#graph-container").width(); // 获取容器宽度
            var height = $("#graph-container").height(); // 获取容器高度

            svg = d3.select("#graph-container").append("svg")
                .attr("width", width)
                .attr("height", height);


            var identity = d3.geoIdentity().reflectY(true);
            // 创建地理路径生成器
            const pathGenerator = d3.geoPath().projection(identity);

            /*计算边界信息，用于初始化缩放*/
            function calculateBounds(coordinates) {
                var bounds = [[Infinity, Infinity], [-Infinity, -Infinity]];

                coordinates.forEach(function (feature) {
                    feature.forEach(function (shape) {
                        shape.forEach(function (coord) {
                            bounds[0][0] = Math.min(bounds[0][0], coord[0]);
                            bounds[0][1] = Math.min(bounds[0][1], -coord[1]);
                            bounds[1][0] = Math.max(bounds[1][0], coord[0]);
                            bounds[1][1] = Math.max(bounds[1][1], -coord[1]);
                        });
                    });

                });

                return bounds;
            }
            // 创建比例尺
            if (scale == Infinity) {
                var bounds = calculateBounds(geojsonData.coordinates);
                var dx = bounds[1][0] - bounds[0][0],
                    dy = bounds[1][1] - bounds[0][1],
                    x = (bounds[0][0] + bounds[1][0]) / 2,
                    y = (bounds[0][1] + bounds[1][1]) / 2;
                scale = Math.min(width / dx, height / dy),
                    translate = [width / 2 - scale * x, height / 2 - scale * y];
            }

            /*墙壁和障碍物绘制*/
            var walls = svg.append("path")
                .datum(geojsonData)
                .attr("transform", "translate(" + translate + ")scale(" + scale + ")")
                .attr("d", pathGenerator)
                .attr("fill", "lightblue") // 设置填充颜色
                .attr("stroke", "black")
                .style("stroke-width", "0.1px"); // 设置边框颜色
            /*标记点绘制*/
            var node_warnings = svg.append("g")
                .attr("class", "warnings")
                .selectAll("circle")
                .data(warnings)
                .enter().append("circle")
                .attr("id", d=>d.client)
                .attr("r", nodeRadius)
                .attr("cx", function (d) { return d.pos[0]; })
                .attr("cy", function (d) { return -d.pos[1]; })
                .style("fill", "orange");

            var node_infusings = svg.append("g")
                .attr("class", "infusings")
                .selectAll("circle")
                .data(infusings)
                .enter().append("circle")
                .attr("id", d=>d.client)
                .attr("r", nodeRadius)
                .attr("cx", function (d) { return d.pos[0]; })
                .attr("cy", function (d) { return -d.pos[1]; })
                .style("fill", "blue");

            var labels = svg.append("g")
                .attr("class", "labels")
                .selectAll("text")
                .data([...warnings, ...infusings])
                .enter().append("text")
                .text(function (d) { return d.client; })  // 设置文字内容
                .style('font-size', '10px')
                .attr("x", function (d) { return d.pos[0]; }) // 设置文字位置
                .attr("y", function (d) { return -d.pos[1]; }) // 调整文字位置
            // 创建缩放行为
            var initialTransform = d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale);
            var zoom = d3.zoom()
                .scaleExtent([0.5, 500]) // 缩放范围
                .on("zoom", zoomed);

            svg.call(zoom).call(zoom.transform, initialTransform);
            // 将缩放行为应用到 svg 元素上
            function zoomed() {
                var currentTransform = d3.event.transform;
                scale = currentTransform.k, translate = [currentTransform.x, currentTransform.y];
                // 计算缩放后的节点半径，连线宽度和标签字号
                var scaledNodeRadius = nodeRadius / currentTransform.k;
                var scaledLinkStrokeWidth = linkStrokeWidth / currentTransform.k;

                // 设置节点的半径，连线的宽度和标签文字的字号
                walls.attr("transform", currentTransform);
                node_warnings.attr("transform", currentTransform)
                    .attr("r", scaledNodeRadius); // 设置节点半径
                node_infusings.attr("transform", currentTransform)
                    .attr("r", scaledNodeRadius); // 设置节点半径
                labels.attr('transform', function (d) {
                    const x = currentTransform.applyX(d.pos[0]);
                    const y = currentTransform.applyY(-d.pos[1]); // 调整label的y坐标，使其在视觉上保持10单位距离
                    return `translate(${x}, ${y})`;
                })
            }
        }
    });
}

//保存之前的缩放值
var scale = Infinity,
    translate = Infinity;
// 初始加载图


//AJAX 请求
function sendData() {
    $.ajax({
        url: '/settarget',
        type: 'POST',
        data: JSON.stringify({
            client: $("#client").val(),
            target: $("#target").val()
        }),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (response) {
            console.log(response);
        }
    });
}

function emphasize(client) {
    currentTransform = d3.event.transform;
    var circle = svg.append("emphasize")
        .attr("cx", currentTransform.x + nodes[client][0] * currentTransform.k) // 设置圆心x坐标
        .attr("cy", currentTransform.y + -nodes[client][1] * currentTransform.k) // 设置圆心y坐标
        .attr("r", 10) // 初始半径
        .style("fill", "none")
        .style("stroke", "#0077b6") // 设置圆环颜色
        .style("stroke-width", 2) // 设置圆环宽度
        .style("opacity", 1); // 初始不透明度
    circle.transition()
        .duration(2000) // 动画持续时间，例如2000毫秒
        .attr("r", 100) // 最终半径
        .style("opacity", 0) // 最终不透明度
        .on("end", function () {
            d3.select(this).remove(); // 动画完成后移除元素
        });
}

$(document).ready(function () {
    $("#floor").change(function () {
        var nowfloor = $("#floor").val();
        var nowclient = $("#client").val();
        updateGraph(nowfloor, nowclient);
    });
    $("#client").change(function () {
        var nowfloor = $("#floor").val();
        var nowclient = $("#client").val();
        updateGraph(nowfloor, nowclient);
    });

    updateGraph($("#floor").val(), $("#client").val());
    setInterval(function () {
        updateGraph($("#floor").val(), $("#client").val());
    }, 2000);
});