(function () {
  var graph;
  $.ajax({
    // TODO: Hardcode this
    url: window.location.href,
    success: function (data) {
      // TODO: Send this to the template
      if (data.status == 'not ready') {
        alert('Your query is not ready');
      }
      else {


        graph = data;
        // determinar el tamaño en el que se va a ver el arbol
        var width = $("#tree").width(),
        height = 600;
        var fill = d3.scale.category10();

        var nodes = [],
        foci = [{x: width/2, y: 280},{x: width/2, y: 190}, {x: width/2, y: 150}];

        var svg = d3.select("#tree").append("svg")
          .attr("width", width)
          .attr("height", height);

        function tick(e) {

          var k = .1 * e.alpha;
          // Push nodes toward their designated focus.
          nodes.forEach(function(o, i) {
            if (o.group == "trunk"){
              o.y += (foci[o.id].y - o.y) * (.1 * e.alpha);
              o.x += (foci[o.id].x - o.x) * (.2 * e.alpha);
            }else{
              o.y += (foci[o.id].y - o.y) * (.1 * e.alpha);
              o.x += (foci[o.id].x - o.x) * k;
            }

          });

          node
            .attr("cx", function(d) { return d.x; })
            .attr("cy", function(d) { return d.y; });
        }

        var force = d3.layout.force()
          .nodes(nodes)
          .links([])
          .gravity(0)
          .size([width, height])
          .on("tick", tick)

          var node = svg.selectAll("circle");


        var max_degree = 0;
        var min_degree = 0;

        graph.nodes.forEach(function(o, i){

          if (parseInt(o.degree) <= min_degree){

            min_degree = o.degree;

          }

          if (parseInt(o.degree) >= max_degree){

            max_degree = o.degree;

          }
        });

        graph.nodes.forEach(function(o, i){
          if (o.group == "root"){
            $("#jsontable tbody").append("<tr class='bg-yellow'><td>"+ o.group+"</td><td>"+ o.label+"</td><td>"+ o.ri+"</td></tr>");
          } else if (o.group == "trunk"){
            $("#jsontable tbody").append("<tr class='bg-red'><td>"+ o.group+"</td><td>"+ o.label+"</td><td>"+ o.ri+"</td></tr>");
          } else if (o.group == "leaf") {
            $("#jsontable tbody").append("<tr class='bg-green'><td>"+ o.group+"</td><td>"+ o.label+"</td><td>"+ o.ri+"</td></tr>");
          }
          
          // agregar el elemento en la lista de todos los nodos
          // desde aca --------------------------->
          var fillcolor = function (node) {
            if (o.group == "root") {
                return "#f5a200"
            }
            if (o.group == "trunk") {
              return "#824d13"
            }
            if (o.group == "leaf") {
              return "#4cac33"
            }
          };
          var data = o.label.split("DOI")

          //armar la redireccion a doi si se tiene doi
          if (data[1]!=null) {
            data[1] = "href='http://dx.doi.org/" + $.trim(data[1])+"' target='_blank'"
          } else{
            data[1] = "href='#!' class='right disabled'"
          };
          // var adoi =
          var litoinsert = $("<li id='nodelist"+o.id +''+o.indice+
              "' class='collection-item'><i class='material-icons circle left' style='color:"+
              fillcolor(o)+
              ";font-size:21px;background:none;'>brightness_1</i>"+
              "<a "+data[1]+"class='right'><i class='material-icons'>link</i></a>"+
              "<p>"+
              data[0]+
              "</p></li>");
          $('.allnodes').prepend(litoinsert);

          //<----------------------------------- hata aca

          if (o.id !=9) {
            nodes.push({id: o.id, group: o.group, label: o.label, indice: o.ri, degree: o.degree });
            force.start();

            node = node.data(nodes);

            node.enter().append("circle")
              .attr("class", "node")
              .attr("id",function(d){
                return d.id+''+d.indice
              })
            .attr("group", function (d) {
              return d.group;
            })
            .attr("label", function (d) {
              return d.label;
            })
            .attr("indice", function (d) {
              return d.indice;
            })
            .attr("cx", function (d) {
              return d.x;
            })
            .attr("cy", function (d) {
              return d.y;
            })
            .attr("r", function (d) {
              var radio = 0;

              parseInt(d.degree)

                var divisor = (max_degree - min_degree)/9;

              radio = (parseInt(d.degree) / parseInt(divisor))+4;

              return radio
            })



            .on("click", function (d, i) {

              var data = d.label.split("DOI")

              if ($('#node'+ d.id +''+d.indice)[0]) {
                //quitar la etiqueta de informacion del nodo deseleccionado
                $('#node'+ d.id +''+d.indice).remove();
                d3.select(this).style("fill",function (node) {
                  if (node.group == "root") {
                    return "#f5a200"
                  }
                  if (node.group == "trunk") {
                    return "#824d13"
                  }
                  if (node.group == "leaf") {
                    return "#4cac33"
                  }
                });

              } else {
                //colocar la etiqueta de informacion del nodo seleccionado
                var fillcolor = function (node) {
                  if (d.group == "root") {
                    return "#f5a200"
                  }
                  if (d.group == "trunk") {
                    return "#824d13"
                  }
                  if (d.group == "leaf") {
                    return "#4cac33"
                  }
                };

                //armar la redireccion a doi si se tiene doi
                if (data[1]!=null) {
                  data[1] = "href='http://dx.doi.org/" + $.trim(data[1])+"' target='_blank'"
                } else{
                  data[1] = "href='#!' class='right disabled'"
                };

                // var adoi =
                var litoinsert = $("<li id='node"+d.id +''+d.indice+
                    "' class='collection-item'><i class='material-icons circle left' style='color:"+
                    fillcolor(d)+
                    ";font-size:21px;background:none;'>brightness_1</i>"+
                    "<a href='#!' data-node='"+d.id +','+d.indice+"' onclick='quit(this)' class='quit-in-list right'><i class='material-icons'>clear</i></a>"+
                    "<a "+data[1]+"class='right'><i class='material-icons'>link</i></a>"+
                    "<p>"+
                    data[0]+
                    "</p></li>");
                d3.select(this).style("fill",function (node) {
                  if (node.group == "root") {
                    return "#a86f00"
                  }
                  if (node.group == "trunk") {
                    return "#351d07"
                  }
                  if (node.group == "leaf") {
                    return "#235f13"
                  }
                });
                $('.selectedNodes').prepend(litoinsert);
              };

            })

            .style("fill", function (d) {
              return fill(d.id);
            })
            .style("fill", function (d) {
              if (d.group == "root") {
                return "#f5a200"
              }
              if (d.group == "trunk") {
                return "#824d13"
              }
              if (d.group == "leaf") {
                return "#4cac33"
              }
            })
            .call(force.drag);

          }

        });//end else
      }//end function ajax
    }//end ajax
  });

})();

function quit (e) {
  nodedata = $(e).data('node').split(',')

    $('#node'+nodedata[0]+''+nodedata[1]).remove();

  d3.select($('#'+nodedata[0]+''+nodedata[1])[0]).style("fill",function (node) {
    if (node.group == "root") {
      return "#f5a200"
    }
    if (node.group == "trunk") {
      return "#824d13"
    }
    if (node.group == "leaf") {
      return "#4cac33"
    }
  });
};



