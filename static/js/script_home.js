// ------------------------------------------------------- //
    // Charts Gradients
    // ------------------------------------------------------ //
    

$(function(){
  'use strict'

  //Courbe sous le nombre de tweets
  if($("#rs3").length != 0) {
    var rs3 = new Rickshaw.Graph({
      element: document.querySelector('#rs3'),
      renderer: 'line',
      series: [{
        data: [
          { x: 0, y: 5 },
          { x: 1, y: 7 },
          { x: 2, y: 10 },
          { x: 3, y: 11 },
          { x: 4, y: 12 },
          { x: 5, y: 10 },
          { x: 6, y: 9 },
          { x: 7, y: 7 },
          { x: 8, y: 6 },
          { x: 9, y: 8 },
          { x: 10, y: 9 },
          { x: 11, y: 10 },
          { x: 12, y: 7 },
          { x: 13, y: 10 }
        ],
        color: '#1B84E7',
      }]
    });
    rs3.render();

    // Responsive Mode
    new ResizeSensor($('.slim-mainpanel'), function(){
      rs3.configure({
        width: $('#rs3').width(),
        height: $('#rs3').height()
      });
      rs3.render();
    });
  }
  
   
});

$( document ).ready(function() {
    
    //rs3 étant sur la meme page
    if($("#rs3").length != 0) {
      //Global feeling
      $.ajax({
        type: "GET",
        url: "/global_feeling",
        success: function(data) {
          $('#progress_neg').css('width', data["neg"]+"%");
          $('#progress_pos').css('width', data["pos"]+"%");
          $('#progress_neu').css('width', data["neu"]+"%");
        }
      });

      //Piechart data
      $.ajax({
        type: "GET",
        url: "/piechartdata",
        success: function(data) {
          let color_tab = "["
          for (let i = 0; i < data["color"].length; i++) {
            color_tab += '"'+data["color"][i] + '",';
          }
          color_tab = color_tab.slice(0,-1);
          color_tab = color_tab+"]";
          
          $( "#repartition" ).append( "<div class=\"mg-b-25\"><span class=\"peity-donut\" data-peity='{ \"fill\": "+color_tab+", \"height\": 200, \"width\": \"100%\" }'>"+data["value"]+"</span></div>" );
          $('.peity-donut').peity('donut');

          let noms = data["candidat"]["nom"];
          let nb_tweets = data["candidat"]["nb_tweets"];

          let indice = 0;
          $.each( noms, function( key, value ) {
            $( "#repartition" ).append("<div class=\"d-flex align-items-center mg-t-5\"><span class=\"square-10 bg-pink rounded-circle\" style=\"background-color: "+data["color"][indice]+";\"></span><span class=\"mg-l-10\">"+noms[indice]+"</span><span class=\"mg-l-auto tx-lato tx-right\">"+nb_tweets[indice]+"</span></div>");
            indice++;
          });
          //
        }
      });

      //Global week activity
      $.ajax({
        type: "GET",
        url: "/globalweekactivity",
        success: function(data) {
          let max = Math.max.apply(Math,data["nbr_tweets"]) + 1000;   
          var ctx1 = document.getElementById('chartBar1').getContext('2d');

          var myChart1 = new Chart(ctx1, {
            type: 'bar',
            data: {
              labels: data["label"],
              datasets: [{
                label: 'tweet(s) téléchargé(s)',
                data: data["nbr_tweets"],
                backgroundColor: '#27AAC8'
              }]
            },
            options: {
              legend: {
                display: false,
                  labels: {
                    display: false
                  }
              },
              scales: {
                yAxes: [{
                  ticks: {
                    beginAtZero:true,
                    fontSize: 10,
                    max: max
                  }
                }],
                xAxes: [{
                  ticks: {
                    beginAtZero:true,
                    fontSize: 11
                  }
                }]
              }
            }
          });
        }
      });
    }

    //Logs
    getLog();
    function getLog() {
      $.ajax({
        type: "GET",
        url: "/getlog",
        success: function(data) {
          if(data["log"].length>0){
            let lg = data["date"];
            let indice = 0;
            $("#list-log").empty();
            $.each( lg, function( key, value ) {
              $( "#list-log" ).append("<div class=\"activity-item\"><div class=\"row no-gutters\"><div class=\"col-2 tx-right\">"+data["date"][indice]+"</div><div class=\"col-2 tx-center\"><span class=\"square-10 bg-danger\"></span></div><div class=\"col-8\">"+data["log"][indice]+"</div></div></div>");
              indice++;
            });
            $( "#bell-notif" ).append("<span class=\"indicator\"></span>");
          }
          
        }
      });
    }   
    var isUpdateactive = 0;
    //Update tweet
    $( "#updateTweet" ).on( "click", function() {
      
      if($("#updateTweet").data("state") == 0 && isUpdateactive == 0){
          
          $( '.update_icon' ).removeClass( 'fa-download' );
          $('.update_icon').addClass("fa-sync fa-spin");
          $("#updateTweet").attr("data-state",1);
          $( "#list-log" ).empty();
          var xhr = $.ajax({
              type: "GET",
              url: "/test",
              success: function(response){
                getLog();
                isUpdateactive = 1;
              }
          });
      }      
    });

    var checkUpdateTweetEndId = setInterval(function() {
      if($("#updateTweet").attr("data-state") && $("#updateTweet").attr("data-state") == 1){
        getLog();
          $.ajax({
              type: "GET",
              url: "/check_updateTweets_state",
              success: function(data) {
                  if(data["statut"]==0){
                      clearInterval(checkUpdateTweetEndId);
                      $( '.update_icon' ).removeClass( 'fa-sync fa-spin' );
                      $('.update_icon').addClass("fa-download");
                      $("#updateTweet").attr("data-state",0);
                      isUpdateactive = 0;
                      getLog();
                      location.reload();
                  }
              },
              error: function(){
                  clearInterval(checkUpdateTweetEndId);
                  getLog();
              }
          });
      }
    }, 50000);

    $( "#deleteLog" ).on( "click", function() {
      $.ajax({
        type: "GET",
        url: "/empty_logs",
        success: function(data) {
          if(data["code"]==200){
            location.reload();
          }
        }
      });
          
    });

    $( "#addCandidat" ).on( "click", function() {
        
      var partipoli = $("#modalInputPartiPolitique").val();
      var urlphoto = $("#modalInputPhoto").val();
      var comptetwitter = $("#modalInputTwitter").val();
      
      function checkImage(imageSrc, good, bad) {
          var img = new Image();
          img.onload = good; 
          img.onerror = bad;
          img.src = imageSrc;
      }
      function good(){ 
          $('#PhotoHelp').text("Le lien de l'image est valide");
          $('#PhotoHelp').css('color', 'green');
          $( '#modalInputPhoto' ).removeClass( 'is-invalid' );
          $('#modalInputPhoto').addClass("is-valid");

          $.ajax({
              type: "GET",
              url: "/add_candidat/?twitter="+comptetwitter+"&parti="+partipoli+"&photo="+urlphoto,
              success: function(data) {
                  if(data['code'] == 200){
                      $( '.update_icon' ).removeClass( 'fa-download' );
                      $('.update_icon').addClass("fa-sync fa-spin");
                      $("#updateTweet").attr("data-state",1);
                      location.reload();
                  }else {
                      $('#TwitterHelp').text(data['message']);
                      $('#TwitterHelp').css('color', '#dc3545');
                      $('#modalInputTwitter').addClass("is-invalid");
                  }
              }
          });
      };
      function bad(){ 
          $('#PhotoHelp').text("Le lien de l'image est invalide");
          $('#PhotoHelp').css('color', '#dc3545'); 
          $('#modalInputPhoto').addClass("is-invalid");
      }
      
      checkImage(urlphoto,  good, bad );
      
    });

    $( "#login").on( "click", function () {
      var username = $("#login-username").val();
      var password = $("#login-password").val();

      $.ajax({
          type: "POST",
          url: "/connexion",
          data:{
              loginUsername: username,
              loginPassword: password
          },
          success: function(data) {
              if(data['code'] == 200){
                  window.location.href = "/";
              }else {
                  $('#errorMessage').text(data['message']);
                  $('#errorMessage').css('color', 'red');
              }
          }
      });
    });

    // ------------------------------------------------------- //
    // Bar Chart
    // ------------------------------------------------------ //
    if($("#ChartWeek").length != 0) {
        var pathname = window.location.pathname;
        var json_url_feelings = "/weekactivity"+pathname;
        var ChartWeek = document.getElementById("ChartWeek");
        
        ajax_week_activity(json_url_feelings);
        
        function ajax_week_activity(url,data) {

            $.getJSON(url, data).done(function(response) {
                var barChartWeek = new Chart(ChartWeek, {
                    type: "bar",
                    options: {
                        scales: {
                            xAxes: [
                                {
                                    display: true,
                                    gridLines: {
                                        color: "#eee",
                                    },
                                },
                            ],
                            yAxes: [
                                {
                                    display: true,
                                    gridLines: {
                                        color: "#eee",
                                    },
                                },
                            ],
                        },
                    },
                    data: {
                        labels: response["label"],
                        datasets: [
                            {
                                label: "Tweets négatifs",
                                backgroundColor: ["#c0392b", "#c0392b", "#c0392b", "#c0392b", "#c0392b", "#c0392b", "#c0392b"],
                                hoverBackgroundColor: ["#c0392b", "#c0392b", "#c0392b", "#c0392b", "#c0392b", "#c0392b", "#c0392b"],
                                borderColor: ["#c0392b", "#c0392b", "#c0392b", "#c0392b", "#c0392b", "#c0392b", "#c0392b"],
                                borderWidth: 1,
                                data: response["data_neg"],
                            },
                            {
                                label: "Tweets positifs",
                                backgroundColor: ["#27ae60", "#27ae60", "#27ae60", "#27ae60", "#27ae60", "#27ae60", "#27ae60"],
                                hoverBackgroundColor: ["#27ae60", "#27ae60", "#27ae60", "#27ae60", "#27ae60", "#27ae60", "#27ae60"],
                                borderColor: ["#27ae60", "#27ae60", "#27ae60", "#27ae60", "#27ae60", "#27ae60", "#27ae60"],
                                borderWidth: 1,
                                data: response["data_pos"],
                            },
                        ],
                    },
                });   
            });
        }

    }

    // ------------------------------------------------------- //
    // Algo Vader
    // ------------------------------------------------------ //
    if($("#ChartVader").length != 0) {
      var pathname = window.location.pathname;
      var json_url_feelings = "/vader"+pathname;
      var CHART_V = document.getElementById("ChartVader");

      ajax_chart_vader(json_url_feelings);
      
      function ajax_chart_vader(url,data) {
          $.getJSON(url, data).done(function(response) {
              
              var feelingsChart2 = new Chart(CHART_V, {
                  type: "doughnut",
                  options: {
                      cutoutPercentage: 40,
                  },
                  data: {
                      labels: response['label'],
                      datasets: [
                          {
                              data: response['data'],
                              borderWidth: 0,
                              backgroundColor: ["#27ae60", "#c0392b", "#95a5a6"],
                              hoverBackgroundColor: ["#27ae60", "#c0392b", "#95a5a6"],
                          },
                      ],
                  },
              });
          
              var feelingsChart2 = {
                  responsive: true,
              };
          });
      }
    }

    // ------------------------------------------------------- //
    // Algo TextBlob
    // ------------------------------------------------------ //
    if($("#ChartTextBlob").length != 0) {
        var pathname = window.location.pathname;
        var json_url_feelings = "/TextBlob"+pathname;
        var CHART_T = document.getElementById("ChartTextBlob");

        ajax_chart_TextBlob(json_url_feelings);
        
        function ajax_chart_TextBlob(url,data) {
            $.getJSON(url, data).done(function(response) {
                
                var feelingsChart3 = new Chart(CHART_T, {
                    type: "doughnut",
                    options: {
                        cutoutPercentage: 40,
                    },
                    data: {
                        labels: response['label'],
                        datasets: [
                            {
                                data: response['data'],
                                borderWidth: 0,
                                backgroundColor: ["#27ae60", "#c0392b", "#95a5a6"],
                                hoverBackgroundColor: ["#27ae60", "#c0392b", "#95a5a6"],
                            },
                        ],
                    },
                });
            
                var feelingsChart3 = {
                    responsive: true,
                };
            });
        }
    }

    // ------------------------------------------------------- //
    // Ajout YouTube Vidéo
    // ------------------------------------------------------ //
    $( "#addVideo" ).on( "click", function() {
        
      var candidat = $("#candidat_id").find(":selected").val();
      var emission = $("#modalInputEmission").val();
      let urlvideo = $("#modalInputVideo").val();
      var parts_url = urlvideo.split("=");
      
      function checkVideo(videoSrc) {
        let matches = videoSrc.match(/watch\?v=([a-zA-Z0-9\-_]+)/);
        if(matches) good();
        else bad();
      }
      function good(){ 
          $('#VideoHelp').text("Le lien de la vidéo est valide");
          $('#VideoHelp').css('color', 'green');
          $( '#modalInputVideo' ).removeClass( 'is-invalid' );
          $('#modalInputVideo').addClass("is-valid");

          $.ajax({
              type: "GET",
              url: "/add_video/?id_youtube="+parts_url[1]+"&emission="+emission+"&candidat_id="+candidat,
              success: function(data) {
                  if(data['code'] == 200){
                    location.reload();
                  }
              }
          });
      };
      function bad(){ 
          $('#VideoHelp').text("Le lien de la vidéo est invalide");
          $('#VideoHelp').css('color', '#dc3545'); 
          $('#modalInputVideo').addClass("is-invalid");
      }
      
      checkVideo(urlvideo);
      
    });

});
