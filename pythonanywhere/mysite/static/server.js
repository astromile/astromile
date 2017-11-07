sendRequest = function(command, params, onLoad) {
    var request = new XMLHttpRequest()
    request.responseType = 'json'
    request.onload = function(e) {
        if (e.target.status == 200) {
            onLoad(e.target.response)
        } else {
            console.log('AJAX request failed [' + e.target.status + ']: ' + e.target.statusText)
        }
    }
    var str = []
    for (var p in params) {
        if (params.hasOwnProperty(p)) {
            str.push(encodeURIComponent(p) + '=' + encodeURIComponent(params[p]))
        }
    }
    var baseUrl = window.location.href
    if (baseUrl.indexOf('localhost') >= 0) {
        baseUrl = "http://127.0.0.1:5000"
    } else {
        baseUrl = baseUrl.substr(0, baseUrl.indexOf('/', baseUrl.lastIndexOf('.')))
    }
    var url = baseUrl + '/' + command + '?' + str.join('&')
    request.open('GET', url, true)
    request.send()
}