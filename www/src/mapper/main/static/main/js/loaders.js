mapper_module.graph = function () {
    $.ajax({
      url: 'api/nodes/article',
      type: 'GET',
      success: function (json) {
        if (!('links' in json))
          json['links'] = []

        const nodes = json.nodes,
          links = json.links
        console.log("Main")
        console.log(json)
        mapper_module.render(nodes, links, mapper_module.canvas)
      },
      error: function (xhr, errormsg, error) {}
    });
  }

  mapper_module.mapper =  function (url = mapperEndpoint) {
    $.ajax({
      url: url,
      type: 'GET',
      success: function (json) {
        if (!('links' in json))
          json['links'] = []

        const nodes = json.nodes,
          links = json.links
        console.log("Mapper")
        console.log(nodes)
        renderMapper(nodes, links)
      },
      error: function (xhr, errormsg, error) {
        console.log(error)
      }
    });

}