function IsPC(){  
    var userAgentInfo = navigator.userAgent;
    var Agents = new Array("Android", "iPhone", "SymbianOS", "Windows Phone", "iPad", "iPod");  
    var flag = true;  
    for (var v = 0; v < Agents.length; v++) {  
        if (userAgentInfo.indexOf(Agents[v]) >= 0) { flag = false; break; }  
    }
    if (userAgentInfo.indexOf("Mozilla") >= 0){
        flag = true;
    }
    return flag;  
}
if (IsPC()){
    window.location.href ="/pc";
}
else{
    window.location.href ="/mobile";
}