    var map; //mapオブジェクト保管用
    var marker; 
    var infoWindow; //吹き出し
    var data = {{data|tojson}}; //main.pyから配列受け取り
    var housedata ={{house_detail|tojson}}; //main.pyからhouselist受け取り


    const list0 = data; //locデータの読み込み
    const houselist =  housedata; //house_detailの読み込み
    const obj = housedata;

    // var mapstyle =  style;      //mapstyle.js読み込みたい  

    //1．位置情報の取得に成功した時の処理
    function mapsStart(position) {

      //lat=緯度、lon=経度 を取得 
      var lat = position.coords.latitude;
      var lon = position.coords.longitude;

      //  オランダの緯度経度をlat2とlon2でセット のちのセンター表示で使用
      var lat2 = 32.995315; 
      var lon2 = 129.758527;

      //div#mapを「GoogleMap」化
      map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: lat2, lng: lon2 }, //緯度,経度を設定
        zoom: 13 //Zoom値設定
        //style 
        // styles:mapstyle
      });


   //配列表記
      var data1 = data; //配列を受け取ってdata1に入れ替え
      // data1.push({lat:'33.005963', lng:'129.814619', name:'無人島田島　片山智弘'});
          //console.log(data1);   //配列の更新確認

    // マーカーの作成（0からデータの数分まで）
    for (i = 0; i < data.length; i++) {
     　create_marker(data[i].lat, data[i].lng);
     }

     // 関数定義 create_marker
      function create_marker(lat, lng){
      　//変数 marker_options
      　var marker_options = {
        　map: map,
        //  icon: 'img/vgboy.png',
         title:'物件',
          position: new google.maps.LatLng(lat, lng)
               };
        // 変数 marker
         var marker = new google.maps.Marker(marker_options);
          //  icon: 'img/maps_pin.png'   
            
         var marker_options2 ={
          
         };
         marker.setOptions(marker_options2);

    //プッシュピンを置く
    const beachMarker = new google.maps.Marker({
      position: new google.maps.LatLng(lat, lng),
        map: map,
      });

        // マーカー吹き出しに追加
        infoWindow = new google.maps.InfoWindow({ // 吹き出しの追加
                            content: '<div class="sample" id="detail">物件詳細をみる</div>' // 吹き出しに表示する内容
                      });
                      beachMarker.addListener('mouseover', function() { // マーカーをクリックしたとき
                      infoWindow.open(map, beachMarker); // 吹き出しの表示
                      }); 
                      beachMarker.addListener('click', function() { // マーカーをクリックしたとき
                      // alert("hey");
                      console.log("IN")
                      // $('body').append('<div class="modal_bg"></div>');
                      // $('.modal_bg').fadeIn();
                            //モーダルイン
                            $('body').append('<div class="modal_bg"></div>');
                            $('.modal_bg').fadeIn();
                              //リスト表示

                    //(ここが表示されない)
                            //モーダルアウト
                                $('.modal_bg, .modal_close').off().click(function(){
                                       $('.modal_box').fadeOut();
                                        $('.modal_bg').fadeOut('slow',function(){
                                          $('.modal_bg').remove();
                                        });
                                 });
                      }); 
                    
           }
    };

    

          //2． 位置情報の取得に失敗した場合の処理
          function mapsError(error) {
            var e = "";
            if (error.code == 1) { //1＝位置情報取得が許可されてない（ブラウザの設定）
              e = "位置情報が許可されてません";
            }
            if (error.code == 2) { //2＝現在地を特定できない
              e = "現在位置を特定できません";
            }
            if (error.code == 3) { //3＝位置情報を取得する前にタイムアウトになった場合
              e = "位置情報を取得する前にタイムアウトになりました";
            }
            alert("エラー：" + e);
          };

          //3.位置情報取得オプション
          var set = {
            enableHighAccuracy: true, //より高精度な位置を求める
            maximumAge: 20000,        //最後の現在地情報取得が20秒以内であればその情報を再利用する設定
            timeout: 10000            //10秒以内に現在地情報を取得できなければ、処理を終了
          };

          //Main:位置情報を取得する処理 //getCurrentPosition :or: watchPosition
          function initMap() {
            navigator.geolocation.watchPosition(mapsStart, mapsError, set);

             
          }





<!-- 物件一覧モーダル ここから-->
  

     

 //consoleで確認用
//  for(var item in obj["househouse1"]){
//       console.log("キー"+item);
//       console.log("値："+obj["househouse1"][item]);
//     }



      $(function(){
     // 「.modal_open」をクリックしたらモーダルと黒い背景を表示する
     $('.modal_open').click(function(){
        
     // 黒い背景をbody内に追加
     $('body').append('<div class="modal_bg"></div>');
     $('.modal_bg').fadeIn();
    //   console.log(list0);
    //    for (i = 0; i < data.length; i++) {
    //      loclist =data[i].loc;
    //      $('.list_class').append("<p>"+loclist+"</p>");
    //   }
    
     //試し 表示 
     for(var item in obj["househouse1"]){
            $('.list_class').append(
              "<table>"
               +"<tr>"
                +"<th>"+"説明"
                +"</th>"
                +"<td>"+obj["househouse1"][item]
                +"</td>"
                +"</tr>"
                +"</table>")
          }


     // data-targetの内容をIDにしてmodalに代入
     var modal = '#' + $(this).attr('data-target');
  
     // モーダルをウィンドウの中央に配置する
     function modalResize(){
         var w = $(window).width();
         var h = $(window).height();
  
         var x = (w - $(modal).outerWidth(true)) / 2;
         var y = (h - $(modal).outerHeight(true)) / 2;
  
         $(modal).css({'left': x + 'px','top': y + 'px'});
     }
  
     // modalResizeを実行
     modalResize();
  
     // modalをフェードインで表示
     $(modal).fadeIn();
  
     // .modal_bgか.modal_closeをクリックしたらモーダルと背景をフェードアウトさせる
     $('.modal_bg, .modal_close').off().click(function(){
         $('.modal_box').fadeOut();
         $('.modal_bg').fadeOut('slow',function(){
             $('.modal_bg').remove();
         });
     });
  
     // ウィンドウがリサイズされたらモーダルの位置を再計算する
     $(window).on('resize', function(){
         modalResize();
     });
  
     // .modal_switchを押すとモーダルを切り替える
     $('.modal_switch').click(function(){
  
       // 押された.modal_switchの親要素の.modal_boxをフェードアウトさせる
       $(this).parents('.modal_box').fadeOut();
  
       // 押された.modal_switchのdata-targetの内容をIDにしてmodalに代入
       var modal = '#' + $(this).attr('data-target');
  
       // モーダルをウィンドウの中央に配置する
       function modalResize(){
           var w = $(window).width();
           var h = $(window).height();
  
           var x = (w - $(modal).outerWidth(true)) / 2;
           var y = (h - $(modal).outerHeight(true)) / 2;
  
           $(modal).css({'left': x + 'px','top': y + 'px'});
       }
  
       // modalResizeを実行
       modalResize();
  
       $(modal).fadeIn();
  
       // ウィンドウがリサイズされたらモーダルの位置を再計算する
       $(window).on('resize', function(){
           modalResize();
       });
     });
   });
 });
