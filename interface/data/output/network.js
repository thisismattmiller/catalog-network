var network = {

    lastMouseMove: null,

    pointerActive: false,
    pointerPoint: null,



   	checkForNode: function(event){


        var osdmouse = OpenSeadragon.getMousePosition(event)        
        point = network.imagingHelper.physicalToDataPoint(osdmouse) 



        // gridX = parseInt(Math.round(point.x / 25) * 25);
        // gridY = parseInt(Math.round(point.y / 25) * 25);

        //console.log(gridX,gridY);

		var myQuery = {
			
		    query: {
		        bool: {
		            must: [
		                {
		                    range: {
		                        x1: {
		                            lte: parseInt(point.x)
		                        } 
		                    }
		                },
		                {
		                    range: {
		                        x2: {
		                            gte: parseInt(point.x)
		                        }
		                    }
		                },
		                {
		                    range: {
		                        y1: {
		                            lte: parseInt(point.y)
		                        }
		                    }
		                },
		                {
		                    range: {
		                        y2: {
		                            gte: parseInt(point.y)
		                        }
		                    }
		                }
		            ]
		        }
		    }    
		

		};



		$.post( "http://107.170.89.213:9200/nodes/node/_search", JSON.stringify(myQuery), function( data ) {


			if (data.hits.total !== 0){
				
				d = data.hits.hits[0]['_source'];

				console.log(d);

				$("#h2-holder h2").text(d['name'])


				$(".subject-info-titles-holder").empty()


				for (x in d.titles){

					t = d.titles[x];

					var bnumber = t.bnumber.replace('.','http://catalog.nypl.org/record=');
					bnumber = bnumber.substring(0,bnumber.length-1);

					var author = (t.author==="") ? "" : " by " + t.author;

					$(".subject-info-titles-holder").append(

						$("<a>")
							.text(t.title + author)
							.attr('href',bnumber)
							.addClass('subject-info-titles')
							.attr('target','_blank'	)

					);



				}

					$(".subject-info-titles-holder").append(

						$("<a>")
							.text("Search NYPL.org for more ")
							.attr('href','http://catalog.nypl.org/search~S1/?searchtype=d&searcharg=' + data.hits.hits[0]['_source']['name'])
							.addClass('subject-info-titles')
							.attr('target','_blank'	)

					);


					$("#subject-info").css("left",0);



			}else{


				$("#subject-info").css("left",-500);


			}
			
		  
		});

   		//network.imagingHelper


   	},

    init: function() {

    	var self = this;


        $("#openseadragon").css({
            height: $(window).height(),
            width: $(window).width()
        });
        network.viewer = OpenSeadragon({
            id: "openseadragon",
            visibilityRatio: 0.1,
            minZoomLevel: 0.5,
            maxZoomLevel: 100,
            zoomPerClick: 1.4,

            prefixUrl: "images/",
            tileSources: "base.dzi"
        });

        network.imagingHelper = network.viewer.activateImagingHelper();


        // $(document).mousemove(function(event) {


        //     self.lastTimeMouseMoved = new Date().getTime();

        //     var t = setTimeout(function() {
        //         var currentTime = new Date().getTime();
        //         if (currentTime - self.lastTimeMouseMoved > 1000) {
        //             self.checkForNode(event)
        //         }
        //     }, 1000)
        // });




		$(document).keyup(function(e) {

		  if (e.keyCode == 27) { self.blurSearch()}   // esc
		});

		$("#openseadragon").click(function(e){ 

			self.blurSearch();

			self.checkForNode(e);

		});



		$("#search").keyup(function(e) {

			clearTimeout(self.t);
			var search = $(this).val();

	        self.t = setTimeout(function() {
	            self.search(search);
	        }, 350)


		});

		$("#search").focus(function() { $(this).select(); $("#search-results").show() });
		$("#search").mouseup(function(e){e.preventDefault();});


		$("#about-label").click(function(){

			if ($("#about").css("bottom").search("-") > -1){

				$("#about").css("bottom",0);

			}else{

				$("#about").css("bottom",-245);

			}

		});


    },

    blurSearch : function(){

    	$("#search").blur()
    	$("#search-results").hide()

    },

    search : function(search){

    	var self = this;

		var myQuery = {
		    query: {
		        query_string: {
		           default_field: "name",
		           query: search
		        }
		    }

		};

		$("#search-results").show().text("Loading...");



		$.post( "http://107.170.89.213:9200/nodes/node/_search", JSON.stringify(myQuery), function( data ) {


			if (data.hits.total !== 0){
				$("#search-results").text("");

				for (x in data.hits.hits){

					d = data.hits.hits[x]['_source'];

					$("#search-results").append(
						$("<a>")
							.text(d.name)
							.attr("href","#")
							.data("d",d)
							.click(function(event){self.subjectLinkClick(event,$(this).data('d'))})

					).append($("<br>"));
					console.log(d);

				}


			}else{
				$("#search-results").text("No results.");

			}
			
		  
		});



    },


    subjectLinkClick : function(e,d){

    	var self = this;


    	console.log(d);

    	network.viewer.viewport.zoomTo(0.5, null, true);

    	point = network.imagingHelper.dataToLogicalPoint({ x: d.x2 , y: d.y2 + (d.size*4) });

    	
    	console.log(point);

    	//network.viewer.viewport.panTo(point, true);

    	setTimeout(function(){

    		
    		network.viewer.viewport.zoomTo(40,point)


  
    		// pointer = network.imagingHelper.dataToPhysicalPoint({ x: d.x1 , y: d.y1 });

    		// setTimeout(function(){
    		// 	$("#pointer").css({ left: pointer.x, top: pointer.y  });
    		// }, 1000);

    	},500);




    	this.blurSearch();

    	e.preventDefault();
    	return false;


    },

    onOsdCanvasMouseMove: function(event) {

    	var self = this;

        var osdmouse = OpenSeadragon.getMousePosition(event),
            osdoffset = OpenSeadragon.getElementOffset(network.viewer.canvas);
        
        //console.log(network.imagingHelper.physicalToDataPoint(osdmouse) )
        // outputVM.OsdMousePositionX(osdmouse.x);
        // outputVM.OsdMousePositionY(osdmouse.y);
        // outputVM.OsdElementOffsetX(osdoffset.x);
        // outputVM.OsdElementOffsetY(osdoffset.y);

        //var offset = _$osdCanvas.offset();
        // outputVM.mousePositionX(event.pageX);
        // outputVM.mousePositionY(event.pageY);
        // outputVM.elementOffsetX(offset.left);
        // outputVM.elementOffsetY(offset.top);
        // outputVM.mouseRelativeX(event.pageX - offset.left);
        // outputVM.mouseRelativeY(event.pageY - offset.top);
        // updateImgViewerScreenCoordinatesVM();
    }



}


$(document).ready(function() {
    network.init();
});