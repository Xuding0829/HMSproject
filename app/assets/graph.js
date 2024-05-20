// 通过D3.js加载和更新图
function updateGraph(floor, client) {
    let baseUrl = "/graph";
    $.ajax({
        url: '/graph', // 服务器端的URL
        type: 'POST', // 请求类型，GET、POST、PUT等
        contentType: 'application/json', // 发送数据的格式
        data: JSON.stringify({
            "floor":floor,
            'client':client,
        }), // 将数据转换为JSON字符串
        success: function (args) {
            var nodeRadius = 5, linkStrokeWidth = 1;
            graphData = args.graphData;
            devicepos = args.devicepos;
            geojsonData = args.obstacle;
            linkdata = args.path;
            // 清空图容器
            d3.select("#graph-container").selectAll("*").remove();
            graphData = JSON.parse(graphData)
            geojsonData = JSON.parse(geojsonData)
            var width = $("#graph-container").width(); // 获取容器宽度
            var height = $("#graph-container").height(); // 获取容器高度

            var svg = d3.select("#graph-container").append("svg")
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
            var scale, translate;
            // 创建比例尺
            if (trans[floor] == undefined) {
                var bounds = calculateBounds(geojsonData.coordinates);
                var dx = bounds[1][0] - bounds[0][0],
                    dy = bounds[1][1] - bounds[0][1],
                    x = (bounds[0][0] + bounds[1][0]) / 2,
                    y = (bounds[0][1] + bounds[1][1]) / 2;
                scale = Math.min(width / dx, height / dy),
                translate = [width / 2 - scale * x, height / 2 - scale * y];
                trans[floor] = [scale, translate]
            }
            else{
                scale = trans[floor][0], translate = trans[floor][1];
            }

            /*路径绘制*/
            var link = svg.append("g")
                .attr("class", "links")
                .selectAll("line")
                .data(linkdata)
                .enter()
                .append("line")
                .style("stroke", "red")
                .attr("x1", function (d) { return d[0][0]; })
                .attr("y1", function (d) { return -d[0][1]; })
                .attr("x2", function (d) { return d[1][0]; })
                .attr("y2", function (d) { return -d[1][1]; });
            /*墙壁和障碍物绘制*/
            var walls = svg.append("path")
                .datum(geojsonData)
                .attr("transform", "translate(" + translate + ")scale(" + scale + ")")
                .attr("d", pathGenerator)
                .attr("fill", "lightblue") // 设置填充颜色
                .attr("stroke", "black")
                .style("stroke-width", "0.1px"); // 设置边框颜色
            /*标记点绘制*/
            var node = svg.append("g")
                .attr("class", "nodes")
                .selectAll("circle")
                .data(graphData.nodes)
                .enter().append("circle")
                .attr("r", 5)
                .attr("cx", function (d) { return d.pos[0]; })
                .attr("cy", function (d) { return -d.pos[1]; });
            /*设备点绘制*/
            if (devicepos != null) {
                var devicenode = svg.append("circle");
                devicenode.attr("class", "device")
                    .attr("r", 5)
                    .attr("cx", devicepos[0])
                    .attr("cy", -devicepos[1])
                    .style("fill", "blue");
            }
            // 为每个顶点添加文字标签
            var labels = svg.append("g")
                .attr("class", "labels")
                .selectAll("text")
                .data(graphData.nodes)
                .enter().append("text")
                .text(function (d) { return d.id; })  // 设置文字内容
                .style('font-size', '15px')
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
                trans[floor] = [scale, translate]
                // 计算缩放后的节点半径，连线宽度和标签字号
                var scaledNodeRadius = nodeRadius / currentTransform.k;
                var scaledLinkStrokeWidth = linkStrokeWidth / currentTransform.k;

                // 设置节点的半径，连线的宽度和标签文字的字号
                walls.attr("transform", currentTransform);
                node.attr("transform", currentTransform)
                    .attr("r", scaledNodeRadius); // 设置节点半径
                if (devicepos != null)
                    devicenode.attr("transform", currentTransform)
                        .attr("r", scaledNodeRadius);
                link.attr("transform", currentTransform)
                    .attr("stroke-width", scaledLinkStrokeWidth); // 设置连线宽度
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
var trans = {};
    scale = Infinity,
    translate = Infinity;


//AJAX 请求
function settarget() {
    $.ajax({
        url: '/settarget',
        type: 'POST',
        data: JSON.stringify({
            client: $("#client").val(),
            target: $("#target").val()
        }),
        success: function (response) {
            nowfloor = $("#floor").val();
            nowclient = $("#client").val();
            updateGraph(nowfloor, nowclient);
        },
        contentType: "application/json; charset=utf-8",
        dataType: "json",
    });
}

$(document).ready(function () {
    // 初始加载图
    updateGraph($("#floor").val(), $("#client").val());
    setInterval(function () {
        updateGraph($("#floor").val(), $("#client").val());
    }, 2000);
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
});