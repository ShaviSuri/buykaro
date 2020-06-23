function remove_cart(){
	$.ajax({
		url:"",
		data:{delete_cart:1},
		success:function(data){
			alert(data);
		}
	})
}
