(function () {
  $(".button-collapse").sideNav();
  $('.modal-trigger').leanModal();
  $('.materialize-textarea').characterCounter();
  // TODO: Ask for pusher details with an ajax query
  if($('#username').length){
    var pusher = new Pusher('ba0d99f4e3c523d40ad1');
    var channelpersonal = 'queries-' + String($('#username').text());
    var channel = pusher.subscribe(channelpersonal);
    channel.bind('tree-created', function (data) {
      // TODO: Do your magic Mateo
      console.log(data.pk);
      console.log(data.url);

      var divtoget = "#Q"+data.pk;
      var csv = "#csvQ"+data.pk;


      $newhtml=$("<a class='btn-floating waves waves-teal' style='opacity:0;' href='"+data.url
        +"'><i class='material-icons'>play_arrow</i></a>");

      $boton=$("<a id='csvQ"+data.pk+"' style='opacity:0;' class='rigth' href='"+data.url+"/"+data.pk
        +"'><i class='material-icons'>file_download</i></a>");

      $(divtoget).children().fadeOut(500,function(){
        $(divtoget).empty();
        $(divtoget).append($newhtml);
        $(divtoget).children().fadeTo(500,1);
        $(divtoget).parent().append($boton)
        $(csv).fadeTo(500,1);

      });
      Materialize.toast("<span>The tree has grown up!</span><a class='btn-flat yellow-text' href='"+data.url+"'><i class='material-icons' style='font-size:30px'>foreward</i><a>", 10000);
    });
  };
})();
