sendRequest = function(command,params,onLoad) {
	var request = new XMLHttpRequest()
	request.responseType='json'
	request.onload = function(e){
		if(e.target.status==200){
			onLoad(e.target.response)
		}else{
			console.log('AJAX request failed [' + e.target.status + ']: ' + e.target.statusText)
		}
	}
	var str = []
	for(var p in params){
		if(params.hasOwnProperty(p)){
			str.push(encodeURIComponent(p) + '=' + encodeURIComponent(params[p]))
		}
	}
	var url = window.location.href+ '/' + command + '?' + str.join('&')
	request.open('GET',url,true)
	request.send()
}


