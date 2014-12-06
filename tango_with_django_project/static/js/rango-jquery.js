$(document).ready(function() {
	// JQuery code to be added in here.
	$("#likes").click(function(){
		var catid;
		catid = $(this).attr("data-catid");
		$.ajax({
			type: "GET",
			url: "/rango/like_category/",
			data: {
				category_id: catid
			},
			contentType: "application/json; charset=UTF-8",
			dataType: "json",
			async: true
		}).fail(function(jqXHR, msg){
			alert(msg);
		}).done(function(data){
			$("#like_count").html(data.likes+" like(s)");
			$("#likes").hide();
		});
	});

	$('#suggestion').keyup(function(){
		var query;
		query = $(this).val();
		$.ajax({
			type: "GET",
			url: "/rango/suggest_category/",
			data: {
				suggestion: query
			},
			async: true
		}).fail(function(jqXHR, msg){
			alert(msg);
		}).done(function(data){
			$("#cats").html(data);
		});
	});
});