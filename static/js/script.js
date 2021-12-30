"use strict";

document.addEventListener("DOMContentLoaded", function () {

    // ------------------------------------------------------- //
    // Charts Gradients
    // ------------------------------------------------------ //
    var canvas = document.querySelector("canvas");

    var ctx1 = canvas.getContext("2d");
    var gradient1 = ctx1.createLinearGradient(150, 0, 150, 300);
    gradient1.addColorStop(0, "rgba(133, 180, 242, 0.91)");
    gradient1.addColorStop(1, "rgba(255, 119, 119, 0.94)");

    var gradient2 = ctx1.createLinearGradient(146.0, 0.0, 154.0, 300.0);
    gradient2.addColorStop(0, "rgba(104, 179, 112, 0.85)");
    gradient2.addColorStop(1, "rgba(76, 162, 205, 0.85)");


    // ------------------------------------------------------- //
    // Pie Chart
    // ------------------------------------------------------ //
    if($("#pieChartExample").length != 0) {
        var json_url = "/piechartdata";
        var PIECHARTEXMPLE = document.getElementById("pieChartExample");

        ajax_chart(json_url);

        function ajax_chart(url,data) {
            
            $.getJSON(url, data).done(function(response) {
                var color_tab = []
                for (let index = 0; index < response['label'].length; index++) {
                    color_tab[index] = "#"+Math.floor(Math.random()*16777215).toString(16);    
                }
                var pieChartExample = new Chart(PIECHARTEXMPLE, {
                    type: "pie",
                    data: {
                        labels: response['label'],
                        datasets: [
                            {
                                data: response['data'],
                                borderWidth: 0,
                                backgroundColor: color_tab,
                                hoverBackgroundColor: color_tab,
                            },
                        ],
                    },
                    options : {
                        responsive: true,
                        title: {
                        display: false
                        },
                        legend: {
                        display: true,
                        position: "bottom",
                        labels: {
                            fontColor: "#333",
                            fontSize: 16
                        }
                        }
                    }
                });
                
                var pieChartExample = {
                    responsive: true,
                };
            });
        }
    }

    // ------------------------------------------------------- //
    // Algo Chart
    // ------------------------------------------------------ //
    if($("#ChartAlgo").length != 0) {
        var pathname = window.location.pathname;
        var json_url_feelings = "/feelings"+pathname;
        var DOUGHNUTCHARTEXMPLE = document.getElementById("ChartAlgo");

        ajax_chart_feelings(json_url_feelings);
        
        function ajax_chart_feelings(url,data) {
            $.getJSON(url, data).done(function(response) {
                
                var feelingsChart1 = new Chart(DOUGHNUTCHARTEXMPLE, {
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
                                backgroundColor: ["#17a589", "#cb4335", "#979a9a"],
                                hoverBackgroundColor: ["#17a589", "#cb4335", "#979a9a"],
                            },
                        ],
                    },
                });
            
                var feelingsChart1 = {
                    responsive: true,
                };
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
                                backgroundColor: ["#17a589", "#cb4335", "#979a9a"],
                                hoverBackgroundColor: ["#17a589", "#cb4335", "#979a9a"],
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
                                backgroundColor: ["#17a589", "#cb4335", "#979a9a"],
                                hoverBackgroundColor: ["#17a589", "#cb4335", "#979a9a"],
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
                                backgroundColor: [gradient1, gradient1, gradient1, gradient1, gradient1, gradient1, gradient1],
                                hoverBackgroundColor: [gradient1, gradient1, gradient1, gradient1, gradient1, gradient1, gradient1],
                                borderColor: [gradient1, gradient1, gradient1, gradient1, gradient1, gradient1, gradient1],
                                borderWidth: 1,
                                data: response["data_neg"],
                            },
                            {
                                label: "Tweets positifs",
                                backgroundColor: [gradient2, gradient2, gradient2, gradient2, gradient2, gradient2, gradient2],
                                hoverBackgroundColor: [gradient2, gradient2, gradient2, gradient2, gradient2, gradient2, gradient2],
                                borderColor: [gradient2, gradient2, gradient2, gradient2, gradient2, gradient2, gradient2],
                                borderWidth: 1,
                                data: response["data_pos"],
                            },
                        ],
                    },
                });   
            });
        }

    }

});

$( document ).ready(function() {
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
    
    $( "#updateTweet" ).on( "click", function() {
        if($("#updateTweet").data("state") == 0){
            $( '.update_icon' ).removeClass( 'fa-download' );
            $('.update_icon').addClass("fa-sync fa-spin");
            $("#updateTweet").attr("data-state",1);

            var xhr = $.ajax({
                type: "GET",
                url: "/test",
                success: function(response){
                    console.log(response);
                }
            });
        
            //xhr.abort(); //kill the request
        }
        
    //$(".loader_div").show();
    /*$.ajax({
        type: "GET",
        url: "/create",
        success: function(data) {
            $(".loader_div").hide();
            location.reload();
        }
    });*/
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

    var checkUpdateTweetEndId = setInterval(function() {
        if($("#updateTweet").attr("data-state") && $("#updateTweet").attr("data-state") == 1){
            $.ajax({
                type: "GET",
                url: "/check_updateTweets_state",
                success: function(data) {
                    if(data["statut"]==0){
                        clearInterval(checkUpdateTweetEndId);
                        $( '.update_icon' ).removeClass( 'fa-sync fa-spin' );
                        $('.update_icon').addClass("fa-download");
                        $("#updateTweet").attr("data-state",0);
                    }
                },
                error: function(){
                    clearInterval(checkUpdateTweetEndId);
                }
            });
        }
      }, 50000); 

    
});
